# Phase 7.1 — current architecture audit (before implementation)

## Findings

- A real backend exists. It is a custom `node:http` server, **not Express**.
- `server/app.js` implements REST routing, authentication, role/ownership checks, and response scoping. `server/security.js` implements native Argon2id and SHA-256 session hashing. `server/rateLimiter.js` implements bounded login throttling.
- `server/database.js` owns SQLite schema migrations 1–5, relational loading, JSON workflow persistence, transactional seed, and workflow/audit atomicity. The persisted source is `server/data/pravaha.sqlite`.
- The React/Vite app currently lives in root `src/` and `public/`. `src/api/client.js` is its only fetch client; components consume that client. Relative `/api` paths rely on Vite's proxy. `TeamLeaderDashboard.jsx` imports one selector from the otherwise server-side workflow service.
- `src/services/projectWorkflowService.js` operates workspace snapshots; `src/services/intelligence/` extraction/scoring/evidence modules are pure and do **not** depend on SQLite.
- Root package scripts start the Node backend. `vite.config.js`, `scripts/dev.js`, `server/config.js`, and `server/index.js` contain local host/port/database fallback assumptions. CORS and seed configuration live in the Node config. `.env.example` currently selects SQLite.
- No Python backend, SQLAlchemy, Alembic, PostgreSQL deployment configuration, or frontend/backend env separation exists. There are 37 Node regression tests (18 API/database/security and 19 intelligence/workflow); build and lint scripts exist.
- The installed Node is 24.21.0, npm 11.19.0. Bundled Python 3.12.14 is accessible. PostgreSQL/Docker/Python are not available through PATH; PostgreSQL was not found in Program Files. PostgreSQL verification needs a separately provisioned local environment.

## Migration decisions and risks

- Preserve camelCase response payloads, endpoint paths, error envelope, roles, UI, and existing stable text IDs. There is no Field Worker role.
- Preserve legacy custom `argon2id$salt$digest` hashes (65536 KiB, 3 passes, parallelism 1) and hashed opaque sessions; Python must read the existing hash format without weakening it.
- Preserve PM decisions, baseline JSON, ordered contributions, review history, audits, and matcher-v1 results. Free-text suggestions never approve; explicit assigned activity actions retain their current pre-review actual reporting behavior.
- PostgreSQL snapshot mutations need a transaction lock and atomic workflow/user/system audits to avoid lost updates. Ownership and response scope must remain server-side.
- SQLite export/import is practical. Back up first, record every table's counts, import in one transaction into an empty migrated PostgreSQL target, validate relationships and payloads, and retain SQLite solely as clearly marked migration data.
- FastAPI/PostgreSQL will be canonical. Node application entrypoints will be retired. Retained JavaScript reference tests are test-only migration parity material; equivalent FastAPI/pytest scenarios must run against PostgreSQL.
- Configuration moves to root/backend/frontend env examples. No real secret is committed; application runtime rejects SQLite URLs. Neon uses the same SQLAlchemy psycopg connection configuration.

This report was written before implementation changes. Existing uncommitted user files will be preserved during the reorganization.
