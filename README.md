# Sales Management System

A small end-to-end sales system: a **FastAPI** backend on **PostgreSQL**, a **React** admin
dashboard, and a **React** salesman web app.

- `backend/` — FastAPI REST API
- `admin-dashboard/` — React admin app (Vite)
- `salesman-app/` — React salesman app (Vite, mobile-first)

## 1. Architecture

### Overview

```
┌──────────────────┐     ┌──────────────────┐
│  Salesman App     │     │  Admin Dashboard  │
│  (React, Vite)    │     │  (React, Vite)     │
└─────────┬─────────┘     └─────────┬─────────┘
          │        HTTPS / JSON               │
          └───────────────┬───────────────────┘
                           ▼
                  ┌──────────────────┐
                  │   FastAPI backend │
                  │  (JWT auth, REST)  │
                  └─────────┬─────────┘
                            │  SQL (SQLAlchemy)
                            ▼
                  ┌──────────────────┐
                  │    PostgreSQL      │
                  └──────────────────┘
```

Both frontends are independent single-page apps that talk to the same backend over a
plain REST/JSON API — there is no server-side rendering or shared frontend code. This
keeps the two apps decoupled: the admin dashboard could be replaced or the salesman
app rebuilt in Flutter later without touching the backend contract.

### Frontend/backend communication

- All requests are JSON over HTTPS, authenticated with a `Bearer <JWT>` header.
- CORS is restricted server-side to the known frontend origins (`CORS_ORIGINS` env var).
- Each frontend stores its JWT in `localStorage` and attaches it via an Axios request
  interceptor; a 401 response clears the token and redirects to `/login`.

### Database structure

Five tables, normalized to 3NF:

| Table | Notes |
|---|---|
| `users` | Salesmen **and** admins, distinguished by a `role` enum. Avoids a parallel `admins` table since the two share every other field. |
| `customers` | Independent of any salesman — any salesman can order for any customer. |
| `products` | Includes `stock_quantity`, decremented atomically when an order is placed. |
| `orders` | Belongs to one `customer` and one `salesman` (the user who created it). Has a `status` enum (`pending` / `confirmed` / `cancelled`) and a denormalized `total_amount` for fast listing/dashboard queries. |
| `order_items` | Line items. Stores a **price snapshot** (`unit_price`) at order time — if the catalog price changes later, historical orders stay accurate. |

Constraints used: primary keys (UUID), foreign keys with `ON DELETE RESTRICT`/`CASCADE`
as appropriate, `CHECK` constraints (non-negative prices/stock, positive quantities), a
`UNIQUE` constraint on `(order_id, product_id)`, and indexes on foreign keys, `sku`,
`status`, and `created_at` (the dashboard's time-series query group-by column).

### Authentication & authorization flow

1. `POST /api/auth/login` (OAuth2 password flow) verifies the bcrypt-hashed password
   and returns a JWT containing the user's id and role, expiring after 12 hours.
2. Every protected endpoint resolves the current user from the JWT via a FastAPI
   dependency (`get_current_user`).
3. Role checks are enforced **in the backend**, not just hidden in the UI:
   - Salesmen can only see and open **their own** orders (`403` on other salesmen's
     orders); their order list is filtered server-side.
   - Only admins can access `/api/dashboard/*`, list all users, create products, or
     change an order's status.
   - Order totals and line-item prices are always computed server-side from the
     current product catalog — a client can send `product_id` + `quantity` but has no
     way to influence price, so a tampered client can't manipulate a total.

## 2. Local setup

### Prerequisites
- Python 3.12+
- Node 20+
- PostgreSQL 14+ running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit DATABASE_URL / SECRET_KEY
createdb sales_db               # or: psql -c "CREATE DATABASE sales_db;"

alembic upgrade head            # apply schema
python -m app.seed              # demo admin + salesmen + customers + products

uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Admin dashboard

```bash
cd admin-dashboard
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000
npm run dev                     # http://localhost:5174
```

### Salesman app

```bash
cd salesman-app
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000
npm run dev                     # http://localhost:5173
```

### Seed / demo credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin123!` |
| Salesman | `jdoe` | `Sales123!` |
| Salesman | `asmith` | `Sales123!` |

## 3. Deployment (Render, free tier — no Docker)

All three services deploy to [Render](https://render.com) using Render's **native
runtimes** — no Docker anywhere in this project.

- **Backend** — Render "Python" web service. Build: `pip install -r requirements.txt`.
  Start: `alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Database** — Render managed PostgreSQL (free plan).
- **Both frontends** — Render static sites (Vite build output, no server needed).

### Why the start command runs the seed script every time

Render's **free tier has no shell access**, so there's no way to log in after
deploy and run a one-off seed command. Instead, `app/seed.py` is written to be
**idempotent** — it checks if any user already exists and does nothing if so — so
it's safe to include in the start command and run on every deploy/restart. First
deploy: seeds demo data. Every deploy after that: no-op.

### One-shot deploy with the Blueprint

The repo includes `render.yaml` at the root. In the Render dashboard: **New → Blueprint**,
point it at this repo, and Render provisions the database, backend, and both static
sites together — no manual service creation needed.

**One manual step after first deploy:** Render can't forward-reference the two static
site URLs into the backend's `CORS_ORIGINS` on the very first pass (they don't exist
yet when the backend first builds). After the first deploy:
1. Copy the live URLs of `sales-admin-dashboard` and `sales-salesman-app` from the
   Render dashboard.
2. On the `sales-backend` service → **Environment**, set `CORS_ORIGINS` to those two
   URLs (comma-separated, no spaces), then **Manual Deploy → Deploy latest commit**.

### Manual deploy (if not using the Blueprint)

1. **Database**: Render → New → PostgreSQL, free plan. Copy the **Internal
   Database URL** once it's ready.
2. **Backend**: Render → New → Web Service → connect this repo → set **Root
   Directory** to `backend`. Runtime: Python 3. Build command:
   `pip install -r requirements.txt`. Start command:
   `alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   Add env vars from `backend/.env.example` (`DATABASE_URL` = the string from step 1,
   `SECRET_KEY` = any random string, `CORS_ORIGINS` left blank for now).
3. **Frontends**: Render → New → Static Site, once for each of `admin-dashboard/`
   and `salesman-app/`. Root directory = that folder. Build command
   `npm install && npm run build`, publish directory `dist`. Add a rewrite rule
   `/*` → `/index.html` (needed for React Router). Set `VITE_API_URL` to the
   backend's URL from step 2.
4. Go back to the backend service, set `CORS_ORIGINS` to the two static site URLs,
   redeploy.

### Free-tier limitations worth knowing

- The backend web service **spins down after 15 minutes of inactivity** and takes
  ~30–60 seconds to wake up on the next request — the first request after idle
  time will be slow, that's expected, not a bug.
- The free PostgreSQL database **expires 90 days after creation** (Render deletes
  it) — fine for an assessment, not for anything long-lived.
- No shell access — see the auto-seed explanation above for why that's handled.

### Where things are deployed

*(Fill in after deploying — see the submission checklist below.)*

| Component | URL |
|---|---|
| Backend API | `https://sales-backend.onrender.com` |
| Admin dashboard | `https://sales-admin-dashboard.onrender.com` |
| Salesman app | `https://sales-salesman-app.onrender.com` |

## 4. Testing

```bash
cd backend
source venv/bin/activate
createdb sales_test_db          # dedicated test database, kept separate from dev data
pytest tests/ -v
```

30 tests across four files:

- **`test_auth.py`** — login success/failure, missing credentials, protected routes
  reject missing/invalid tokens, `/me` returns the authenticated user.
- **`test_orders.py`** — order totals are computed from server-side catalog prices
  (not client input), a client can't tamper with price by injecting extra fields,
  zero-quantity and unknown-customer/product requests are rejected, insufficient
  stock is rejected with a clear message, stock is correctly decremented, and a
  created order shows up in the salesman's history.
- **`test_authorization.py`** — a salesman cannot view or list another salesman's
  orders (`403`), an admin sees orders across all salesmen, salesmen are blocked from
  admin-only endpoints (dashboard metrics, product creation, user listing, order
  status changes) while admins can access them.
- **`test_validation.py`** — malformed login/customer/product payloads return `422`,
  duplicate SKUs return `409`, unknown order IDs return `404`, empty order item lists
  are rejected.

Each test runs against a real PostgreSQL test database (`sales_test_db`) with the
schema recreated fresh per test for isolation — this exercises the actual Postgres
constraints (uniqueness, checks) rather than mocking them away.

## 5. What's incomplete / would change for production

In the interest of prioritizing working → correct → tested → secure → deployable
within the assessment window, the following were deliberately scoped out:

- **Refresh tokens** — the JWT is a single long-lived (12h) access token. In
  production I'd add a short-lived access token + refresh token pair.
- **Rate limiting / brute-force protection** on the login endpoint.
- **Pagination** — list endpoints cap at 200 rows via `LIMIT` rather than true
  cursor/offset pagination, fine for assessment-scale data, not for a large catalog.
- **Soft-delete / audit trail** on orders and catalog changes.
- **Native mobile app** — the salesman client is a responsive React web app rather
  than a Flutter APK, per the assessment's "another suitable frontend technology"
  allowance; a PWA manifest would be the next step for an installable, offline-capable
  version.
