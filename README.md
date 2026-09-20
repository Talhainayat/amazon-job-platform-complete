# amazon-job-platform

A legitimate job opportunity management platform for 100+ candidates: candidate
management, job monitoring through permitted sources, rule-based matching,
application tracking, and admin/candidate dashboards.

**Compliance boundary (by design):** this system does not store Amazon (or any
employer) passwords or session cookies, does not bypass CAPTCHA or anti-bot
protections, does not perform unauthorized scraping or automated logins, and
does not auto-claim jobs or auto-book interviews. Job sources are pluggable
through a `JobSource` interface so only permitted/official feeds get wired in.
Candidate-controlled actions (applying, confirming interviews) stay under the
candidate's control.

---

## Architecture

```
amazon-job-platform/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entrypoint
│   │   ├── core/              # config (env vars), security (JWT/hashing)
│   │   ├── db/                 # SQLAlchemy engine/session/base
│   │   ├── models/            # SQLAlchemy ORM models (8 tables)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/v1/             # route modules (auth, candidates, jobs, ...)
│   │   ├── services/           # matching engine, notifications, AI (optional)
│   │   ├── job_sources/        # pluggable JobSource interface
│   │   └── workers/            # Celery app + background tasks
│   ├── alembic/                # DB migrations
│   ├── tests/                  # pytest suite (22 tests)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/              # Login, Dashboard, Jobs, Profile
│       ├── layouts/            # nav shell
│       ├── services/api.ts     # typed API client (axios + JWT)
│       ├── hooks/useAuth.tsx   # auth context
│       └── components/         # ProtectedRoute
├── .env.example
├── setup.ps1 / start_backend.ps1 / start_frontend.ps1
└── README.md (this file)
```

### Core tables
`users`, `candidates`, `candidate_preferences`, `jobs`, `matches`,
`applications`, `notifications`, `audit_logs`, `contact_inquiries` — see
`backend/app/models/`.

### Matching engine
Rule-based, configurable via environment variables (`MATCH_WEIGHT_LOCATION`,
`MATCH_WEIGHT_JOB_TYPE`, `MATCH_WEIGHT_SHIFT`, `MATCH_WEIGHT_OTHER`; default
40/25/20/15 = 100). Returns a score plus matched/unmatched criteria. An
optional AI service (`app/services/ai_service.py`) can layer on top later —
the app never depends on it; it works standalone.

---

## Prerequisites

- Python 3.12
- Node.js 18+ and npm
- Git
- **Optional for now:** PostgreSQL (defaults to SQLite if not set up) and
  Redis (only needed to actually run Celery background workers)

---

## Installation (Windows / PowerShell)

From the project root:

```powershell
.\setup.ps1
```

This creates/reuses `venv`, installs backend dependencies, copies
`.env.example` to `.env` (if missing), runs Alembic migrations, and runs
`npm install` for the frontend. See **Manual steps** below if you'd rather
run each piece yourself.

### Environment variables

Copy `.env.example` to `.env` and adjust as needed. Key variables:

| Variable | Purpose | Local default |
|---|---|---|
| `DATABASE_URL` | DB connection string | SQLite file, zero setup |
| `SECRET_KEY` | JWT signing key | **change this** before any real use |
| `REDIS_URL` / `CELERY_BROKER_URL` | Background job queue | only needed for Celery |
| `AI_API_KEY` / `AI_PROVIDER` | Optional AI matching | blank = rule-based only |
| `EMAIL_ENABLED` + `SMTP_*` | Optional email notifications | disabled by default |

Never commit a real `.env` file.

### Database setup

**SQLite (default, no install needed):** works out of the box; `alembic
upgrade head` creates `backend/job_platform.db`.

**PostgreSQL (production-like):**
1. Install PostgreSQL locally.
2. Create a database and user.
3. Set `DATABASE_URL=postgresql://user:password@localhost:5432/job_platform` in `.env`.
4. Run `alembic upgrade head` from `backend/`.

### Migrations

```powershell
cd backend
alembic upgrade head          # apply
alembic revision --autogenerate -m "message"   # create a new migration after model changes
alembic downgrade -1          # roll back one step
```

---

## Running the app

**Backend:**
```powershell
.\start_backend.ps1
```
Serves at `http://127.0.0.1:8000` — Swagger UI at `/docs`.

**Frontend:**
```powershell
.\start_frontend.ps1
```
Serves at `http://127.0.0.1:5173` (Vite proxies `/api` to the backend).

For a separately deployed frontend, set `VITE_API_BASE_URL` to the public API
base URL, for example `https://api.example.com/api`, before running `npm run
build`. The frontend client uses a 15-second request timeout and displays a
recoverable fallback if a render error reaches the application boundary.

### Production container

The backend includes `backend/Dockerfile` for Hugging Face Spaces, Render, or
another container host:

```powershell
docker build -t job-platform-api ./backend
docker run --rm -p 7860:7860 --env-file .env job-platform-api
```

The image listens on `PORT` when supplied and otherwise uses `7860`. Configure
`ENV=production`, `DEBUG=false`, a strong random `SECRET_KEY`, explicit
`CORS_ORIGINS`, and `SEED_DEMO_DATA=false` in production. The application
rejects insecure production settings during startup instead of silently
running with development defaults.

Health checks are available at `GET /health`; interactive API documentation is
available at `/docs`.

**Redis + Celery (optional, only if you want background job processing):**
```powershell
# Terminal 1 - Redis (requires Redis installed locally, e.g. via WSL or Memurai on Windows)
redis-server

# Terminal 2 - Celery worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

---

## Testing

```powershell
cd backend
pytest -v
```

Covers: health endpoint and error responses, auth (register/login/me),
candidate CRUD + preferences, job CRUD + duplicate detection, matching engine
scoring, and application tracking. Run `pytest -q` from `backend/` to see the
current count.

---

## API overview

Routes are namespaced under `/api`:
`/api/auth`, `/api/candidates`, `/api/jobs`, `/api/matches`,
`/api/applications`, `/api/notifications`, `/api/admin`, and the public
`/api/contact/inquiries` form endpoint.
Full interactive docs at `/docs` once the backend is running.

---

## Development workflow

1. Change a model → `alembic revision --autogenerate -m "..."` → review the
   generated migration → `alembic upgrade head`.
2. Add/modify a route → update the matching Pydantic schema → add a test in
   `backend/tests/`.
3. Run `pytest` before committing.
4. Frontend changes: `npm run dev` for hot reload, `npm run build` to check
   for type errors before shipping.

---

## Testing status (read this before relying on anything below)

**1. Fully tested in this sandbox (verified working, not just written):**
- Backend: all 22 pytest tests passing (auth, candidates, jobs, matching,
  applications, health)
- Backend: live uvicorn server smoke-tested over real HTTP (`/`, `/health`,
  `/docs`, `/api/auth/register`)
- Alembic: initial migration generated, applied to SQLite, and downgrade
  verified
- Celery: `celery_app` and all three tasks import cleanly (proves the code
  is valid Python and correctly wired) — **not** run against a live broker,
  see item 3
- Frontend: `npm install` and `npm run build` both succeed with zero
  TypeScript errors; `npm run dev` smoke-tested (dev server returns HTTP 200)

**2. Prepared but requires testing on your machine:**
- Full backend + frontend running together (this sandbox tested them
  separately; CORS/proxy config is in place but not exercised end-to-end
  through a browser)
- PowerShell scripts (`setup.ps1`, `start_backend.ps1`, `start_frontend.ps1`)
  — written for Windows PowerShell but only sanity-checked by reading, not
  executed, since this sandbox is Linux
- Login/register/dashboard/jobs/profile pages working in an actual browser
  against the real backend
- Alembic migration against real PostgreSQL (only tested against SQLite here)

**3. Not tested — external services unavailable in this sandbox:**
- PostgreSQL: no Postgres server available here; all DB testing used SQLite.
  The models/migrations are standard SQLAlchemy/Alembic and should work
  against Postgres, but this wasn't verified against a live instance.
- Redis / Celery workers: no Redis available here. Task code imports and
  registers correctly, but no task has actually been executed against a
  live broker.
- Email sending: `EMAIL_ENABLED=false` by default; SMTP code path exists
  but was not exercised against a real mail server.
