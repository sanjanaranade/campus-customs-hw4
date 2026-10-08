# Campus Customs — AI for Managers HW4

Campus Customs is a Yale-inspired merchandise shop with a Vite/React/TypeScript frontend, a FastAPI backend, and a PydanticAI shopping guide. Shoppers can browse catalogue items, open product details, create accounts, log in, ask database-backed price and stock questions, and receive clickable product cards from chat.

## Repository layout

```text
AI for Managers/HW 4/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── frontend/                 # Vite + React + TypeScript app
├── backend/                  # FastAPI entry point and agent files
│   ├── main.py
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/prompt.md
└── output/                   # harness, design, usability, app check, audit trail
```

## Required local data pack

The database and catalogue images are intentionally excluded from GitHub. Before running the app, place the supplied local files here:

```text
data/campus_customs.db
data/products/<catalogue image files>
```

The database must contain the `catalogue`, `inventory`, and `users` tables. The backend reads catalogue image paths from the database and serves the matching local files through `/media/products/`.

## Environment setup

From this project directory, create a local environment file without committing it:

```bash
cp .env.example .env
```

Fill in a real Portkey key locally. `PORTKEY_API_KEY` is required for agent chat. `CAMPUS_CUSTOMS_MODEL` may be set to the approved GPT-5.6/GPT-6-series model available through the Portkey account. Use a long random value for `CAMPUS_CUSTOMS_SESSION_SECRET`.

Install backend dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\\Scripts\\activate` instead.

## Run the backend

The required Uvicorn command is launched from `backend/`:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

If the virtual environment is not activated, use `../.venv/bin/uvicorn main:app --reload --port 8000` from `backend/`. The API loads the root `../.env`, `../data/campus_customs.db`, and `../data/products/` automatically.

Useful routes include:

- `GET /api/health` — service check.
- `GET /api/products` and `GET /api/products/{product_id}` — catalogue and detail data.
- `POST /api/auth/register` and `POST /api/auth/login` — account flow.
- `POST /api/chat` — PydanticAI shopping chat with `{message, history, page_context}`.
- `GET /api/chat/history` — saved chat for an authenticated user; guests are not persisted.

## Run the frontend

In a second terminal, from `frontend/`:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open the Vite URL shown in the terminal, normally `http://127.0.0.1:5173`. The Vite development proxy forwards `/api` and `/media` to FastAPI. To use another backend URL, set `VITE_API_URL` in the local `.env` before starting Vite.

Build the production frontend from `frontend/` with:

```bash
npm run build
```

## Safety and public-repository rules

Never commit `.env`, the real Portkey key, `data/`, the SQLite database, or catalogue product images. `.gitignore` protects those paths. `.env.example` contains placeholders only. The required app-check screenshots remain under `output/app_check_images/`; they are documentation images, not catalogue data. `output/audit_trail.json` is intentionally committed with short, redacted records and is preserved append-only by the backend.

New account passwords are stored as Argon2 hashes; the supplied legacy seed format is upgraded after a successful local login. Chat product facts come from SQLite tools rather than model memory, and the full agent safety rules live in `backend/prompts/prompt.md`.

## Submission

After confirming the local app works and checking that no secrets or local data are staged, create a public GitHub repository, push this project, and submit that repository's public URL to Canvas.
