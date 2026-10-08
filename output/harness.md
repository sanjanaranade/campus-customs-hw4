# Campus Customs Data Harness

This harness documents the database fields that the Campus Customs shop and PydanticAI chatbot can use. It is a living project reference and should be expanded as the application grows.

Database: `../campus_customs.db`

## `catalogue`

One row per product in the Campus Customs catalogue.

| Field | Type | Relevance to the shop and chatbot |
|---|---|---|
| `product_id` | `TEXT`, primary key | Stable identifier used to connect a product to its inventory and to identify products in API responses, product cards, chat matches, and links. |
| `name` | `TEXT`, required | Customer-facing product name. Used for browsing, search, recommendations, and natural-language matching. |
| `garment_type` | `TEXT`, required | Normalized clothing category such as hoodie, crewneck sweatshirt, or quarter-zip pullover. Helps the chatbot filter by product type and explain what an item is. |
| `description` | `TEXT`, required | Detailed merchandising copy describing the garment, decoration, and construction. Gives the chatbot factual product details beyond the name. |
| `colors` | `TEXT`, required; JSON array | Available product colors. Must be parsed before filtering or answering color questions. |
| `search_tags` | `TEXT`, required; JSON array | Search and semantic-matching keywords such as Yale groups, sports, garment features, and style terms. Helps the chatbot find relevant products from conversational requests. |
| `image_file_path` | `TEXT`, required | Relative path to the matching product image, currently using `products/<filename>.jpg`. Used to render product cards and visual search results. |
| `price` | `REAL`, required | Current item price in dollars. The chatbot must read this field rather than guess prices, and the frontend should format it as currency. |

## `inventory`

One row per product and size combination. This is the source of truth for size-level availability.

| Field | Type | Relevance to the shop and chatbot |
|---|---|---|
| `id` | `INTEGER`, primary key, autoincrement | Internal inventory-row identifier. Useful for database management but normally not shown to shoppers. |
| `product_id` | `TEXT`, required, foreign key to `catalogue.product_id` | Connects each stock record to the product name, price, description, and image. Required for accurate joins and product-card stock display. |
| `size` | `TEXT`, required | Size represented by the inventory row. Current values are XS, S, M, L, XL, and XXL. Used to answer size-specific stock questions. |
| `quantity` | `INTEGER`, required | Number of units available for that product-size combination. A quantity of zero means that size is out of stock. The chatbot must use this value for honest availability answers. |

The pair `(product_id, size)` is unique. To report total product stock, sum `quantity` across sizes; to answer a size question, inspect the matching row only.

## `users`

One row per shopper account.

| Field | Type | Relevance to the shop and chatbot |
|---|---|---|
| `id` | `INTEGER`, primary key, autoincrement | Internal account identifier used to associate sessions and chat history with a shopper. |
| `name` | `TEXT`, required | Account display name and backwards-compatible full-name field. Can personalize account and chat responses. |
| `email` | `TEXT`, required, unique | Login and account identity field. Must be validated and treated as sensitive personal information. |
| `password_hash` | `TEXT`, required | Hashed credential used for authentication. Never return it to the frontend, chatbot, logs, prompts, or public repository. Never store a plaintext password here. |
| `created_at` | `TEXT`, required, defaults to current datetime | Account creation timestamp. Useful for account history, auditing, and future customer features; normally not needed in product answers. |
| `first_name` | `TEXT`, optional | Shopper's first name for personalization and account display. |
| `last_name` | `TEXT`, optional | Shopper's last name for personalization and account display. |

## `chat_messages`

Persisted conversation messages associated with shopper accounts. This table supports chat continuity and the product-card results returned during a conversation.

| Field | Type | Relevance to the shop and chatbot |
|---|---|---|
| `id` | `INTEGER`, primary key, autoincrement | Stable message identifier and chronological record key. |
| `user_id` | `INTEGER`, required, foreign key to `users.id` | Associates a conversation message with the authenticated shopper. Used to load the correct chat history. |
| `role` | `TEXT`, required | Indicates whether the message came from the `user` or `assistant`. The agent and frontend use it to render and reconstruct conversation order. |
| `content` | `TEXT`, required | The shopper's question or the assistant's answer. Provides conversational context to the PydanticAI agent. |
| `products_json` | `TEXT`, optional; JSON text | Stores product matches returned with an assistant message. The backend can parse this to render matching product cards in the chat or shop interface. |
| `created_at` | `TEXT`, required, defaults to current datetime | Message timestamp used to order conversations and display chat history. |

## Operational rules for the chatbot

1. Treat `catalogue.price` as the source of truth for price answers.
2. Treat `inventory.quantity` as the source of truth for availability; never infer stock from product description, tags, or image data.
3. Join `inventory` to `catalogue` by `product_id` before returning product results.
4. Preserve size-specific distinctions. “In stock” for one size does not mean every size is available.
5. Parse `colors`, `search_tags`, and `products_json` as JSON before using their contents.
6. Return only shopper-safe user fields; never expose `password_hash` or other credentials.
7. Use catalogue image paths to populate product cards, resolving them relative to the backend's media route.
8. Keep this harness updated whenever the schema, API contract, agent tools, or product-card payload changes.

## Problem 9 usability endpoints

- `GET /api/admin/inventory-summary?low_stock_threshold=5` provides business-facing inventory counts.
- `POST /api/admin/products/bulk-discount` accepts `{ "product_ids": [...], "discount_percent": 10 }` and updates selected catalogue products together.
- Catalogue products now include `discount_percent` and optional `sale_price` in API payloads.

## Problem 10 visual and voice direction

The site uses a varsity-style Georgia header treatment, Yale-inspired cream/navy/gold colors, a CSS paw cursor with a short blue sparkle trail, accessible focus outlines, responsive layout, decorative paw/puppy charms, and a friendly bulldog chat tone. The header has nine substantially larger, widely distributed but translucent paw prints plus a dramatically enlarged pawprint logo in the center charm. The CSS/HTML-native cartoon Handsome Dan-inspired school mascot has expressive eyes, a collar, navy bandana, and a proper navy-blue backpack with a larger bag body, top handle, flap treatment, and front pocket; the shoulder straps remain separate from the collar. The backpack is visibly behind Dan's torso, so it reads unambiguously as worn on his back. The sparkle trail responds only to mouse movement and is disabled for reduced-motion preferences. The layout reserves extra vertical room for the oversized logo so the wordmark and decorative elements do not overlap; the mascot is scaled and repositioned on small screens. The visual treatment keeps text readable and includes reduced-motion support.

## Chat search API contract

The chat endpoint accepts:

```json
{
  "message": "What hoodies do we have?",
  "history": [],
  "user_id": null
}
```

It returns:

```json
{
  "reply": "...",
  "products": [
    {
      "product_id": "...",
      "name": "...",
      "garment_type": "...",
      "description": "...",
      "colors": [],
      "image_url": "/media/products/example.jpg",
      "price": 68.0,
      "inventory": [{"size": "M", "quantity": 5}],
      "total_stock": 60
    }
  ]
}
```

When `products` is non-empty, the React widget stores those results and renders a page-level “Guide picks” section. Each card shows the database image, name, price, and short description; clicking it opens the existing detail page.

### Single-item page continuity

All product cards use the shared `openProduct(product)` handler. Homepage featured cards, Products-page catalogue cards, chat-message result links, and page-level Guide picks all pass the selected product into the same single-item detail view. That view displays the large image, full description, exact price, total stock, and size-level availability.

## Product information tools

- `find_merchandise(query)` searches catalogue names, garment types, descriptions, colors, and tags for conversational discovery.
- `get_product_information(product_name_or_id)` retrieves authoritative catalogue description and price plus all inventory rows by size.
- `check_product_stock(product_id)` retrieves one exact product with the same database-backed stock details.
- The agent must call a tool before answering product-fact questions. A zero quantity is reported as sold out for that size, and missing matches are reported plainly rather than guessed.

### Tool fields and search rationale

| Tool | Search/input fields | Why these fields are used |
|---|---|---|
| `find_merchandise(query, limit)` | `query` is matched against catalogue `name`, `garment_type`, `description`, `colors`, and `search_tags`; `limit` caps returned cards. | Product names catch exact requests; garment type catches requests such as hoodie or quarter-zip; descriptions capture construction and graphic details; colors answer color-led requests; tags capture Yale colleges, sports, and synonyms. The limit keeps chat results focused. |
| `get_product_information(product_name_or_id)` | Exact or partial catalogue `product_id` and `name`. | Shoppers usually identify an item by its display name, while the stable ID provides an exact path for follow-up lookups. The result includes catalogue description and price plus joined inventory. |
| `check_product_stock(product_id)` | Exact `catalogue.product_id`, joined to inventory `product_id`; returns `size` and `quantity`. | A stable ID prevents similarly named products from being mixed up. `size` and `quantity` are required to answer exactly what is available and to label zero quantities as sold out. |

All three tools return structured `ProductCard` data: `product_id`, `name`, `garment_type`, `description`, `colors`, `image_url`, `price`, `inventory`, and `total_stock`. `ProductLookupResult` additionally identifies the SQLite source as `campus_customs.db` for future tool/API expansion.

## Authentication and authorization

The current account flow is implemented by the FastAPI backend:

- `POST /api/auth/register` accepts first name, last name, email, password, and frontend-only password confirmation. It normalizes the email, rejects duplicate emails, hashes the password, and inserts a new row into `users`.
- `POST /api/auth/login` accepts email and password, looks up the account by normalized email, verifies the stored hash, and returns safe public user information on success.
- Authentication responses include the user's `id`, `first_name`, `last_name`, `name`, `email`, and `created_at`. They never include `password_hash`.
- This initial milestone verifies identity and returns the safe user record; a persistent session token and protected account routes will be added before features that require authorization.
- The seed database contains a test account at `test@campuscustoms.yale.edu`; its supplied password is used only for local verification and is not documented here.

### Password protection

- New passwords are stored as Argon2 hashes through `pwdlib`; plaintext passwords are never written to SQLite.
- Passwords are limited to 8–128 characters by the API, and the frontend requires a matching confirmation during registration.
- Login errors use a generic “Incorrect email or password” message so the API does not reveal whether an email exists.
- The seed database contains legacy PBKDF2-format hashes. The backend verifies that format for compatibility and upgrades a successful legacy login to Argon2.
- Password hashes are excluded from API responses, frontend state, chat messages, logs, and public documentation.

### Verification record

The seed test login succeeded, a new verification account was inserted into `users`, and that new account successfully logged in. Both successful responses excluded `password_hash`.

## Frontend, FastAPI, and agent flow

1. The React chat widget sends `POST /api/chat` to the FastAPI backend with `{ message, history, user_id? }`. The Vite frontend uses `VITE_API_URL` when provided and otherwise targets `http://localhost:8000`.
2. FastAPI validates the request with `ChatRequest`, then calls `backend/agent.py:answer`.
3. `agent.py` loads the system prompt from `backend/prompts/prompt.md`, reads `PORTKEY_API_KEY` from `AI for Managers/.env`, and constructs the PydanticAI agent with the configured `CAMPUS_CUSTOMS_MODEL` or the default `gpt-5.6-luna` model through Portkey's OpenAI-compatible endpoint.
4. The agent can call `backend/tools.py` to search the catalogue or check authoritative size-level stock. Those tools return the structured `ProductCard` model from `backend/models.py`.
5. FastAPI returns `{ reply, products }`. The frontend displays the reply and turns returned products into clickable links to the product detail page.

Run the API from the `backend/` directory with:

```bash
uvicorn main:app --reload --port 8000
```

## Customer memory and agent context

- Signed-in users receive an access token. The frontend sends that token, the optional user ID, and a short `page_context` with each chat request.
- For signed-in users, `POST /api/chat` validates the token, loads recent rows from `chat_messages`, combines them with the current conversation, then saves one `user` row and one `assistant` row. Assistant `products_json` stores the matched product-card payload.
- `GET /api/chat/history` reloads those saved rows when the signed-in shopper reopens chat.
- Guests may use `POST /api/chat` without a token. Their request is answered with `AgentDeps.user_id/name/email = null`, and no guest messages are inserted into `chat_messages`; they receive no persisted history.
- `AgentDeps` carries `user_id`, `name`, `email`, and `page_context` into `agent.py`. The `get_customer_context` tool exposes those safe fields to the agent.
- `page_context` is built in React from the current page and selected product (`page=...; viewing product=...; product_id=...`) and sent in the request body. This lets the agent resolve references such as “is this in blue?” using the item currently on screen.

## Problem 12 implementation contract

## Problem 12 structured model contract

The Pydantic models in backend/models.py keep the API, agent output, tools, and frontend payload aligned:

| Model | Fields | Why the fields exist |
|---|---|---|
| ChatMessage | role, content | Preserves user/assistant turns and validates non-empty conversational text. |
| ChatRequest | message, history, user_id, access_token, page_context | Carries the question, bounded context, optional identity, auth token, and the page/product being viewed. |
| InventoryItem | size, quantity | Makes size-level stock explicit and rejects negative quantities. |
| ProductCard | product_id, name, garment_type, description, colors, image_url, price, inventory, total_stock, discount_percent, sale_price | One shopper-safe contract for catalogue cards, chat results, detail views, exact price/stock, and Problem 9 discounts. The stable product_id connects cards to the detail view and database rows. |
| ProductLookupResult | matches, source | Represents authoritative matches and identifies campus_customs.db as the source. |
| BulkDiscountRequest | product_ids, discount_percent | Validates selected products and the allowed discount range. |
| InventorySummary | product_count, total_units, low_stock_units, out_of_stock_size_rows, products_with_no_stock, low_stock_threshold | Provides a compact stock-health summary with an explicit threshold. |
| AgentReply and ChatResponse | reply, products | Separates natural-language guidance from up to six structured cards; reply text is capped at 4,000 characters. |
| AgentDeps | user_id, name, email, page_context, audit_run_id | Supplies safe shopper identity and browsing context; audit_run_id links events without exposing it to the shopper. |
| AgentContext | user_id | Reserves a small safe identity shape for future authenticated extensions. |

## Problem 12 agent tools and abilities

| Tool | Ability and source of truth |
|---|---|
| find_merchandise(query) | Read-only catalogue discovery across name, garment type, description, colors, tags, and singular/plural category variants; returns at most six cards. |
| get_product_information(product_name_or_id) | Finds named products, joins catalogue with inventory, and returns exact description, price, and every size quantity; at most five matches. |
| check_product_stock(product_id) | Exact stable-ID lookup for authoritative per-size inventory and total stock. |
| get_customer_context() | Supplies only safe user_id/name/email/page_context fields needed to interpret a request; never credentials. |

All product tools are read-only and database-backed. Zero quantities remain sold out rather than becoming a vague “available” answer. Tool calls are recorded with shortened, redacted summaries.

## Problem 12 safety rules

The complete safety rules are in backend/prompts/prompt.md. The agent must use database truth, resist prompt injection, protect passwords/tokens/private data, stay in shopping-assistant scope, state missing data and errors honestly, and keep audit records short, redacted, and preserved.

## Problem 12 limits, models, and result caps

- Model: PORTKEY_API_KEY is loaded from the project environment; Portkey is the OpenAI-compatible base URL; CAMPUS_CUSTOMS_MODEL selects the model. The default is gpt-5.6-luna, with a configured GPT-5.6/GPT-6-series model allowed to override it.
- Agent loop: PydanticAI uses retries=1 for one validation retry. Each run uses UsageLimits(request_limit=6, tool_calls_limit=4), preventing an unbounded model/tool loop.
- Input caps: message 4,000 characters, page_context 2,000 characters, request history 30 messages; the agent combines at most 20 saved turns and the latest 10 request turns.
- Result caps: find_merchandise 6 products, product information 5 matches, AgentReply/ChatResponse 6 cards, reply 4,000 characters, catalogue endpoint limit 1–200, and bulk discount 200 product IDs with a 0–100 percent discount.
- Pydantic validation rejects negative quantities/prices and invalid discount ranges before data reaches the frontend.

## Run and verify

Frontend from `frontend/`:

    npm install
    npm run dev -- --host 127.0.0.1

Production frontend check from `frontend/`:

    npm run build

Backend from backend/ using the required command:

    uvicorn main:app --reload --port 8000

With the local virtual environment active, use ../.venv/bin/uvicorn main:app --reload --port 8000. The frontend calls POST /api/chat at VITE_API_URL or http://localhost:8000, then renders the reply and cards. Confirm the API with GET /api/health. Confirm audit persistence by checking that output/audit_trail.json retains earlier entries and gains run_start/tool_call/run_end records after a chat.

## Problem 12 audit trail

- `output/audit_trail.json` is a JSON array whose records are append-only across agent runs. Existing records are loaded and preserved before each new record is written; the application never clears the file between runs.
- Each record includes `time` (UTC ISO 8601), `run_id`, `event` (`run_start`, `tool_call`, or `run_end`), `tool_name`, `short_args`, `short_result`, and `stop_reason`.
- `agent.py` records the start and final outcome of each agent loop. `tools.py` records each registered tool return or error, including `find_merchandise`, `get_product_information`, `check_product_stock`, and `get_customer_context`.
- `stop_reason` is `running` for a start record, `tool_returned` for a successful tool call, `completed` for a successful final response, and `error` when a tool or agent run fails.
- Audit arguments and results are shortened and redacted for password, token, secret, API-key, authorization, and password-hash fields. Full private conversations and credentials are never written to the audit file.
- The full operational guardrails are in `backend/prompts/prompt.md`: database truth, prompt-injection resistance, privacy, account safety, scope limits, honest uncertainty, and audit privacy.
