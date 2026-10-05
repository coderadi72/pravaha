# PRAVAHA FastAPI backend

Run commands from the repository root. Python 3.11+ and PostgreSQL are required.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
# Configure root .env or backend/.env using the example; set DATABASE_URL.
python -m alembic -c backend/alembic.ini upgrade head
# New demo DB only, with explicit SEED_* values:
python -m scripts.seed
python scripts/run_backend.py --reload
```

For existing data, use `python -m scripts.migrate_sqlite --source <legacy-file>`
instead of seeding an empty migrated database. Never reset an existing database.

API_HOST/API_PORT control Uvicorn. DATABASE_URL controls SQLAlchemy/psycopg.
CORS_ORIGINS controls allowed exact frontend origins. Development `/docs` and
`/openapi.json` expose Pydantic contracts; `/api/health` verifies database access.
Process env overrides backend/.env, which overrides root .env. Secrets remain private.

Routes use injected sessions with one request transaction. Services enforce
actor-ID role/organization/project/team/submitter ownership. Repositories lock
organizations and flush workflow plus human/system audits atomically. Pure
intelligence services do not access SQL, HTTP, SQLite or JavaScript runtimes.
SQLAlchemy entities are defined once in app/models/entities.py; Alembic revisions
are frozen schema changes. DB_SCHEMA is strict with no fallback to public.

```powershell
$env:TEST_DATABASE_URL = 'YOUR_DEDICATED_POSTGRESQL_TEST_URL'
python -m pytest backend/tests -q
```

Tests create/remove only unique isolated schemas. Do not point test configuration
at the application database. Full setup, API routes, cookies/security, migration,
limitations and future Neon configuration are in the [root README](../README.md).


Phase 8 adds `services/execution_intelligence.py` (pure calculations),
`services/project_intelligence_service.py` (authorization/lifecycle),
`db/intelligence_repository.py` (bounded project inputs and SQL memory pagination),
`api/routes/intelligence.py`, and `schemas/intelligence.py`.
Alembic head is `0002_execution_warnings`; existing Phase 7 services remain unchanged.
See root README for rules, API contracts, configuration and capacity limits.
