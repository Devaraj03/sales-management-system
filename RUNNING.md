# Running This Project — Full Command Reference

Every command needed to get this running, from a clean machine, in order.
No Docker is used anywhere in this project.

---

## 0. Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 14+ installed and running

Check what you have:

```bash
python3 --version
node --version
psql --version
```

---

## 1. Get the code

```bash
unzip sales-management-system.zip -d sales-management-system
cd sales-management-system
```

(Or if you're working from the git repo instead of the zip: `git clone <your-repo-url> && cd sales-management-system`)

---

## 2. Database setup

Create the two databases (one for the app, one dedicated to the test suite):

```bash
createdb sales_db
createdb sales_test_db
```

If `createdb` isn't on your PATH or you get a permission error, use `psql` directly instead:

```bash
psql -U postgres -c "CREATE DATABASE sales_db;"
psql -U postgres -c "CREATE DATABASE sales_test_db;"
```

If you don't know your local Postgres username/password, the default on most
installs is user `postgres` with a password you set at install time — update
`backend/.env` accordingly in the next step.

---

## 3. Backend

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows (PowerShell): venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and set DATABASE_URL to match your local Postgres user/password, e.g.:
#   DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/sales_db

# Apply the database schema
alembic upgrade head

# Load demo data (one admin, two salesmen, customers, products)
python -m app.seed

# Start the API
uvicorn app.main:app --reload --port 8000
```

Leave this running. Confirm it's up in another terminal:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","environment":"development"}
```

Interactive API docs: open `http://localhost:8000/docs` in a browser.

### Demo credentials (after seeding)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin123!` |
| Salesman | `jdoe` | `Sales123!` |
| Salesman | `asmith` | `Sales123!` |

---

## 4. Admin Dashboard

Open a **new terminal** (leave the backend running):

```bash
cd sales-management-system/admin-dashboard

npm install

cp .env.example .env
# .env should contain: VITE_API_URL=http://localhost:8000

npm run dev
```

Open `http://localhost:5174` in a browser. Log in with the `admin` credentials above.

---

## 5. Salesman App

Open **another new terminal**:

```bash
cd sales-management-system/salesman-app

npm install

cp .env.example .env
# .env should contain: VITE_API_URL=http://localhost:8000

npm run dev
```

Open `http://localhost:5173` in a browser. Log in with the `jdoe` or `asmith`
credentials above. It's a mobile-first layout — resize your browser narrow, or
open dev tools' device toolbar, to see it as intended.

---

## 6. Running the tests

Backend terminal (or a new one, with the venv activated):

```bash
cd sales-management-system/backend
source venv/bin/activate          # if not already active

pytest tests/ -v
```

Expected: `30 passed`.

The test suite uses `sales_test_db` (created in step 2) — it drops and
recreates the schema before every single test function, so it never touches
your `sales_db` dev data and each test starts from a clean slate.

To run just one file, e.g. authorization tests only:

```bash
pytest tests/test_authorization.py -v
```

---

## 7. Building the frontends for production (optional, local check)

To confirm both frontends build cleanly before deploying:

```bash
cd admin-dashboard && npm run build && cd ..
cd salesman-app && npm run build && cd ..
```

Each produces a `dist/` folder. You can preview the production build locally with:

```bash
cd admin-dashboard && npx serve dist
cd salesman-app && npx serve dist
```

---

## 8. Stopping everything

```bash
# In each terminal running a dev server, press:
Ctrl+C

# To drop the databases if you want a clean slate later:
dropdb sales_db
dropdb sales_test_db
```

---

## 9. Deploying (Render, free tier, no Docker, no shell access)

See `README.md` section 3 for the full explanation. Quick version:

1. Push this repo to GitHub.
2. Render dashboard → **New → Blueprint** → select your repo. Render reads
   `render.yaml` at the project root and creates the database, backend, and
   both frontends automatically — no manual service setup, no Dockerfiles.
3. After the first deploy finishes, copy the two static site URLs and paste
   them into the backend service's `CORS_ORIGINS` environment variable, then
   redeploy the backend from the Render dashboard (**Manual Deploy → Deploy
   latest commit**). This one step can't be automated because the static
   sites don't have URLs yet on the very first deploy pass.
4. No further commands needed — the backend's start command
   (`alembic upgrade head && python -m app.seed && uvicorn ...`) applies
   migrations and seeds demo data automatically on every deploy, since the
   free tier has no shell access to run it manually.
