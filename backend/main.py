"""Small Campus Customs API foundation.

This layer deliberately keeps the database access straightforward. The future
PydanticAI agent can call these same catalogue and inventory functions without
duplicating the shop's source-of-truth logic.
"""

import json
import base64
import hashlib
import hmac
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from dotenv import load_dotenv

try:
    from .agent import answer
    from .models import AgentDeps, BulkDiscountRequest, ChatMessage, ChatRequest, ChatResponse, InventorySummary
except ImportError:  # Supports `uvicorn main:app` from the backend directory.
    from agent import answer
    from models import AgentDeps, BulkDiscountRequest, ChatMessage, ChatRequest, ChatResponse, InventorySummary


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "campus_customs.db"
PRODUCTS_PATH = BASE_DIR / "data" / "products"
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env", override=False)
SESSION_SECRET = os.getenv("CAMPUS_CUSTOMS_SESSION_SECRET", "local-development-session-secret")

app = FastAPI(title="Campus Customs API", version="0.1.0")
# Argon2 is preferred for new accounts; PBKDF2 support preserves compatibility
# with the supplied seed users without weakening newly stored passwords.
password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify current Argon2 hashes and the supplied seed DB's legacy PBKDF2 format."""
    if stored_hash.startswith(("pbkd$", "pbkdf2_sha256$")):
        _, salt, expected = stored_hash.split("$", 2)
        actual = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), 120_000).hex()
        return hmac.compare_digest(actual, expected)
    return password_hash.verify(plain_password, stored_hash)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/media/products", StaticFiles(directory=PRODUCTS_PATH), name="product-images")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_catalogue_discount_column() -> None:
    with get_connection() as connection:
        fields = {row["name"] for row in connection.execute("PRAGMA table_info(catalogue)").fetchall()}
        if "discount_percent" not in fields:
            connection.execute("ALTER TABLE catalogue ADD COLUMN discount_percent REAL NOT NULL DEFAULT 0")
            connection.commit()


ensure_catalogue_discount_column()


def parse_json_array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def product_from_row(row: sqlite3.Row, inventory: list[dict[str, Any]]) -> dict[str, Any]:
    discount = float(row["discount_percent"] or 0) if "discount_percent" in row.keys() else 0
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": parse_json_array(row["colors"]),
        "search_tags": parse_json_array(row["search_tags"]),
        "image_file_path": row["image_file_path"],
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
        "discount_percent": discount,
        "sale_price": round(row["price"] * (1 - discount / 100), 2) if discount else None,
        "inventory": inventory,
        "total_stock": sum(item["quantity"] for item in inventory),
    }


def load_product(product_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        inventory_rows = connection.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY "
            "CASE size WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3 "
            "WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6 ELSE 7 END",
            (product_id,),
        ).fetchall()
        inventory = [dict(item) for item in inventory_rows]
        return product_from_row(row, inventory)


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    return {"id": row["id"], "first_name": row["first_name"], "last_name": row["last_name"], "name": row["name"], "email": row["email"], "created_at": row["created_at"]}


def issue_session(user_id: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"user_id": user_id, "issued": int(time.time())}).encode()).decode().rstrip("=")
    signature = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def session_user(access_token: str | None) -> sqlite3.Row | None:
    if not access_token or "." not in access_token:
        return None
    payload, signature = access_token.split(".", 1)
    expected = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        user_id = int(data["user_id"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
    with get_connection() as connection:
        return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "campus-customs-api"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str | None = Header(default=None)) -> ChatResponse:
    token = request.access_token or (authorization.removeprefix("Bearer ").strip() if authorization else None)
    user = session_user(token)
    if request.user_id and user and request.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Chat identity does not match the signed-in user")
    memory: list[Any] = []
    if user:
        with get_connection() as connection:
            saved = connection.execute("SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user["id"],)).fetchall()
        memory = [{"role": row["role"], "content": row["content"]} for row in reversed(saved)]
    combined_history = [ChatMessage(**item) for item in memory] + request.history[-10:]
    deps = AgentDeps(user_id=user["id"] if user else None, name=user["name"] if user else None, email=user["email"] if user else None, page_context=request.page_context)
    try:
        result = await answer(request.message, combined_history, deps)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail="The Campus Customs guide is temporarily unavailable") from error
    if user:
        with get_connection() as connection:
            connection.executemany("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", [(user["id"], "user", request.message, None), (user["id"], "assistant", result.reply, json.dumps([product.model_dump() for product in result.products]))])
            connection.commit()
    return ChatResponse(reply=result.reply, products=result.products)


@app.get("/api/chat/history")
def chat_history(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = session_user(authorization.removeprefix("Bearer ").strip() if authorization else None)
    if user is None:
        return {"messages": []}
    with get_connection() as connection:
        rows = connection.execute("SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 30", (user["id"],)).fetchall()
    messages = []
    for row in reversed(rows):
        try:
            products = json.loads(row["products_json"]) if row["products_json"] else []
        except json.JSONDecodeError:
            products = []
        messages.append({"role": row["role"], "content": row["content"], "products": products, "created_at": row["created_at"]})
    return {"messages": messages}


@app.post("/api/auth/register", status_code=201)
def register(request: RegisterRequest) -> dict[str, Any]:
    first_name, last_name = request.first_name.strip(), request.last_name.strip()
    email = str(request.email).strip().lower()
    if not first_name or not last_name:
        raise HTTPException(status_code=422, detail="First and last name are required")
    with get_connection() as connection:
        if connection.execute("SELECT id FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise HTTPException(status_code=409, detail="An account with that email already exists")
        cursor = connection.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{first_name} {last_name}", email, password_hash.hash(request.password), first_name, last_name))
        connection.commit()
        row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"user": public_user(row), "access_token": issue_session(row["id"]), "message": "Account created successfully"}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict[str, Any]:
    email = str(request.email).strip().lower()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
    if row is None or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if row["password_hash"].startswith(("pbkd$", "pbkdf2_sha256$")):
        with get_connection() as connection:
            connection.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash.hash(request.password), row["id"]))
            connection.commit()
    return {"user": public_user(row), "access_token": issue_session(row["id"]), "message": "Login successful"}


@app.get("/api/products")
def list_products(
    search: str | None = Query(default=None, description="Search product names, tags, descriptions, or categories"),
    limit: int = Query(default=100, ge=1, le=200),
) -> dict[str, Any]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM catalogue ORDER BY name").fetchall()

    products = []
    search_term = search.lower().strip() if search else None
    for row in rows:
        searchable = " ".join(
            [row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]
        ).lower()
        if search_term and search_term not in searchable:
            continue
        product = load_product(row["product_id"])
        if product:
            products.append(product)
            if len(products) >= limit:
                break
    return {"products": products, "count": len(products)}


@app.get("/api/admin/inventory-summary", response_model=InventorySummary)
def inventory_summary(low_stock_threshold: int = Query(default=5, ge=0, le=100)) -> InventorySummary:
    with get_connection() as connection:
        totals = connection.execute("SELECT COUNT(DISTINCT product_id) product_count, COALESCE(SUM(quantity), 0) total_units, SUM(quantity <= ?) low_stock_units, SUM(quantity = 0) out_of_stock_size_rows FROM inventory", (low_stock_threshold,)).fetchone()
        no_stock = connection.execute("SELECT COUNT(*) FROM (SELECT product_id FROM inventory GROUP BY product_id HAVING SUM(quantity) = 0)").fetchone()[0]
    return InventorySummary(product_count=totals["product_count"], total_units=totals["total_units"], low_stock_units=totals["low_stock_units"] or 0, out_of_stock_size_rows=totals["out_of_stock_size_rows"] or 0, products_with_no_stock=no_stock, low_stock_threshold=low_stock_threshold)


@app.post("/api/admin/products/bulk-discount")
def bulk_discount(request: BulkDiscountRequest) -> dict[str, Any]:
    ids = list(dict.fromkeys(request.product_ids))
    with get_connection() as connection:
        existing = {row[0] for row in connection.execute(f"SELECT product_id FROM catalogue WHERE product_id IN ({','.join('?' for _ in ids)})", ids).fetchall()}
        missing = [product_id for product_id in ids if product_id not in existing]
        if missing:
            raise HTTPException(status_code=404, detail={"message": "Some products were not found", "missing_product_ids": missing})
        connection.execute(f"UPDATE catalogue SET discount_percent = ? WHERE product_id IN ({','.join('?' for _ in ids)})", [request.discount_percent, *ids])
        connection.commit()
    return {"updated_product_ids": ids, "updated_count": len(ids), "discount_percent": request.discount_percent}


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    product = load_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
