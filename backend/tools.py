"""Database tools available to the Campus Customs agent."""

import json
import os
import sqlite3
import sys
import tempfile
import threading
import types
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if "opentelemetry._events" not in sys.modules:
    events_module = types.ModuleType("opentelemetry._events")
    class Event:
        def __init__(self, *args, **kwargs):
            self.args, self.kwargs = args, kwargs
    class EventLogger:
        def emit(self, *args, **kwargs):
            return None
    class EventLoggerProvider:
        def get_event_logger(self, *args, **kwargs):
            return EventLogger()
    events_module.Event = Event
    events_module.EventLogger = EventLogger
    events_module.EventLoggerProvider = EventLoggerProvider
    events_module.get_event_logger_provider = lambda: EventLoggerProvider()
    sys.modules["opentelemetry._events"] = events_module

from pydantic_ai import RunContext

try:
    from .models import AgentDeps, InventoryItem, ProductCard
except ImportError:  # Supports imports when Uvicorn is launched from backend/.
    from models import AgentDeps, InventoryItem, ProductCard


AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
_AUDIT_LOCK = threading.Lock()
_SENSITIVE_KEYS = {"password", "password_hash", "access_token", "api_key", "authorization", "token", "secret"}


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def _safe_value(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _safe_value(value.model_dump())
    if isinstance(value, dict):
        return {str(key): "[redacted]" if str(key).lower() in _SENSITIVE_KEYS or "password" in str(key).lower() else _safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value[:8]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _short(value: Any, limit: int = 320) -> str:
    text = json.dumps(_safe_value(value), ensure_ascii=False, separators=(",", ":"), default=str)
    return text if len(text) <= limit else f"{text[:limit - 14]}...[shortened]"


def append_audit(*, run_id: str, event: str, tool_name: str, args: Any, result: Any, stop_reason: str) -> None:
    """Append one short, redacted record without dropping prior records."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now(timezone.utc).isoformat(), "run_id": run_id, "event": event, "tool_name": tool_name, "short_args": _short(args), "short_result": _short(result), "stop_reason": stop_reason}
    with _AUDIT_LOCK:
        existing = json.loads(AUDIT_PATH.read_text(encoding="utf-8")) if AUDIT_PATH.exists() else []
        if not isinstance(existing, list):
            raise RuntimeError("output/audit_trail.json must contain a JSON array")
        existing.append(record)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=AUDIT_PATH.parent, delete=False) as temporary:
            json.dump(existing, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary_path = temporary.name
        os.replace(temporary_path, AUDIT_PATH)


DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def _product(row: sqlite3.Row, stock: list[InventoryItem]) -> ProductCard:
    discount = float(row["discount_percent"] or 0) if "discount_percent" in row.keys() else 0
    sale_price = round(row["price"] * (1 - discount / 100), 2) if discount else None
    return ProductCard(
        product_id=row["product_id"], name=row["name"], garment_type=row["garment_type"],
        description=row["description"], colors=_array(row["colors"]),
        image_url=f"/media/{row['image_file_path']}", price=row["price"],
        inventory=stock, total_stock=sum(item.quantity for item in stock), discount_percent=discount, sale_price=sale_price,
    )


def _stock(connection: sqlite3.Connection, product_id: str) -> list[InventoryItem]:
    rows = connection.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY "
        "CASE size WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3 "
        "WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6 ELSE 7 END",
        (product_id,),
    ).fetchall()
    return [InventoryItem(size=row["size"], quantity=row["quantity"]) for row in rows]


def search_catalogue(query: str, limit: int = 6) -> list[ProductCard]:
    """Find products by name, category, description, color, or catalogue tags."""
    words = []
    for word in query.lower().split():
        if len(word) <= 1:
            continue
        variants = {word}
        if word.endswith("ies") and len(word) > 3:
            variants.add(f"{word[:-3]}ie")
        elif word.endswith("s") and len(word) > 2:
            variants.add(word[:-1])
        words.append(variants)
    with _connection() as connection:
        rows = connection.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        matches: list[ProductCard] = []
        for row in rows:
            haystack = " ".join([row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]).lower()
            if not words or all(any(variant in haystack for variant in variants) for variants in words):
                matches.append(_product(row, _stock(connection, row["product_id"])))
            if len(matches) >= limit:
                break
        return matches


def get_product(product_id: str) -> ProductCard | None:
    """Return one product with authoritative size-level stock."""
    with _connection() as connection:
        row = connection.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        return _product(row, _stock(connection, product_id)) if row else None


def lookup_product_info(query: str) -> list[ProductCard]:
    """Look up authoritative product description, price, and per-size stock."""
    normalized = query.strip().lower()
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM catalogue WHERE lower(product_id) = ? OR lower(name) = ? "
            "OR lower(name) LIKE ? ORDER BY name LIMIT 5",
            (normalized, normalized, f"%{normalized}%"),
        ).fetchall()
        return [_product(row, _stock(connection, row["product_id"])) for row in rows]


def _run_tool(ctx: RunContext[AgentDeps], tool_name: str, args: dict[str, Any], operation: Any) -> Any:
    try:
        result = operation()
    except Exception as error:
        if ctx.deps.audit_run_id:
            append_audit(run_id=ctx.deps.audit_run_id, event="tool_call", tool_name=tool_name, args=args, result=str(error), stop_reason="error")
        raise
    if ctx.deps.audit_run_id:
        append_audit(run_id=ctx.deps.audit_run_id, event="tool_call", tool_name=tool_name, args=args, result=result, stop_reason="tool_returned")
    return result


def register_tools(agent: Any) -> None:
    """Register database tools on an agent instance."""
    @agent.tool
    def find_merchandise(ctx: RunContext[AgentDeps], query: str) -> list[ProductCard]:
        return _run_tool(ctx, "find_merchandise", {"query": query}, lambda: search_catalogue(query))

    @agent.tool
    def check_product_stock(ctx: RunContext[AgentDeps], product_id: str) -> ProductCard | None:
        return _run_tool(ctx, "check_product_stock", {"product_id": product_id}, lambda: get_product(product_id))

    @agent.tool
    def get_product_information(ctx: RunContext[AgentDeps], product_name_or_id: str) -> list[ProductCard]:
        return _run_tool(ctx, "get_product_information", {"product_name_or_id": product_name_or_id}, lambda: lookup_product_info(product_name_or_id))

    @agent.tool
    def get_customer_context(ctx: RunContext[AgentDeps]) -> dict[str, str | int | None]:
        """Return the safe identity and page context for the current shopper."""
        return _run_tool(ctx, "get_customer_context", {}, lambda: {"user_id": ctx.deps.user_id, "name": ctx.deps.name, "email": ctx.deps.email, "page_context": ctx.deps.page_context})
