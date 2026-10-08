"""Pydantic request and response types shared by the API and agent."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)
    user_id: int | None = None
    access_token: str | None = None
    page_context: str = Field(default="", max_length=2000)


class InventoryItem(BaseModel):
    size: str
    quantity: int = Field(ge=0)


class ProductCard(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    image_url: str
    price: float = Field(ge=0)
    inventory: list[InventoryItem] = Field(default_factory=list)
    total_stock: int = Field(ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    sale_price: float | None = Field(default=None, ge=0)


class ProductLookupResult(BaseModel):
    """Explicit structured return type for product-information tools."""

    matches: list[ProductCard] = Field(default_factory=list)
    source: str = "campus_customs.db"


class BulkDiscountRequest(BaseModel):
    product_ids: list[str] = Field(min_length=1, max_length=200)
    discount_percent: float = Field(ge=0, le=100)


class InventorySummary(BaseModel):
    product_count: int
    total_units: int
    low_stock_units: int
    out_of_stock_size_rows: int
    products_with_no_stock: int
    low_stock_threshold: int


class AgentReply(BaseModel):
    reply: str = Field(max_length=4000)
    products: list[ProductCard] = Field(default_factory=list, max_length=6)


class ChatResponse(BaseModel):
    reply: str = Field(max_length=4000)
    products: list[ProductCard] = Field(default_factory=list, max_length=6)


class AgentContext(BaseModel):
    """Safe context reserved for future authenticated agent runs."""

    user_id: int | None = None


class AgentDeps(BaseModel):
    """Per-request shopper and browsing context available to the agent/tools."""

    user_id: int | None = None
    name: str | None = None
    email: str | None = None
    page_context: str = ""
    audit_run_id: str | None = None
