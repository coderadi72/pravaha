# PHASE 7.1 AUDIT

Audit date: 2026-10-04. Result: COMPLETE. Phase 8 NOT STARTED.
No deployment or additional AI feature was introduced.

## 1. Current architecture before migration

A real custom Node `node:http` backend existed; it was not Express. Native SQLite
with migrations 1–5 persisted the workflow. React/Vite lived at the root and
called relative `/api` through a Vite proxy. Pure JS intelligence had no SQLite
dependency. The pre-implementation findings are in `phase-7.1-before-audit.md`.
A coherent SQLite backup, row counts and source archive were captured before moves
under `.migration-backups/phase7-20261004-041348/` (ignored/private).

## 2. Final architecture

React/Vite → central env client → FastAPI/Pydantic → service layer → SQLAlchemy
2.x/psycopg → PostgreSQL. Alembic is the schema authority. Node API startup was
removed. Original JS code remains solely as a test reference; no frontend or
application startup imports it. PostgreSQL is mandatory at API runtime.

## 3. Frontend structure

`frontend/src`, `frontend/public`, `frontend/index.html`, package and Vite config.
The existing Phase 7 UI was compared with the pre-change source archive. Changes
are limited to the centralized API client, TL selector import, and the responsive
Home header fix; a new API config module and frontend selector were added.
No dashboard redesign occurred.

## 4. FastAPI backend structure

`backend/app/{api,core,models,schemas,services,db}`, canonical `main.py`, and
`backend/tests`. Routes are thin orchestration with injected sessions. Models
are defined once in `models/entities.py`. Contracts retain camelCase fields.
Pure extraction/scoring/confidence/evidence/workflow modules do not access SQL,
HTTP, SQLite or Node. No empty placeholder automation modules were introduced.

## 5. Database structure

All required entities persist with stable text IDs, JSONB, timezone timestamps,
primary/foreign keys, unique/case-insensitive email and assignment constraints,
role checks and lookup indexes. Canonical database has 24 foreign keys.
TeamLeaderAssignment is the authoritative leader relation. Review history has an
internal insertion sequence to retain equal-timestamp event order. Organization
locks serialize snapshot writes, preventing concurrent lost updates.
Eight ownership/role/organization consistency queries returned zero violations;
see `phase-7.1-consistency.json`. Full original-row comparison passed again after
all tests/runtime checks (`phase-7.1-canonical-data-check.json`).

## 6. API configuration

`frontend/src/api/config.js` resolves the required VITE_API_BASE_URL. Every fetch
uses the central client with credentials included. Alternate API/frontend ports
52975/52974 were used without any component code edit. Five client/configuration
unit tests passed, including missing/unsafe URL and error handling.

## 7. Environment variables

Root, frontend and backend examples exist with blank secrets/passwords. Process
env overrides backend env then root env; Vite loads frontend/root env and process
overrides. DATABASE_URL, CORS, bind ports, frontend API URL, cookie policy and seed
configuration are documented. JWT_SECRET/SESSION_SECRET are reserved, unused
placeholders: opaque sessions remain canonical. Git ignores actual env files,
local credentials, SQLite inputs, venv, PostgreSQL tools, caches, logs and builds.
Private PostgreSQL secret scan found zero values in shareable repository files.
Defaults such as API_PORT=8000 are overridable configuration defaults. Other
localhost/credentials/SQLite occurrences belong to examples, docs, test fixtures,
configuration access or explicit legacy import/reference code.

## 8. PostgreSQL status

PASS: PostgreSQL 18.6 ran locally at a configured port using a non-superuser app
role. Canonical preserved data is in `pravaha_phase71`; tests used `pravaha_test`,
and HTTP/browser mutations used `pravaha_runtime`. The original SQLite remains
unchanged. A prior affected local imported copy (`pravaha`) is retained for
diagnostics, never used as the canonical target. See the failure disclosure below.
No database was dropped/reset. The local PostgreSQL cluster remains available;
its binaries/data/config are ignored machine artifacts under `.tools` / `.audit`.

## 9. Alembic migration status

PASS: upgrade head executed on canonical, dedicated runtime and isolated test
schemas. `current` reports `0001_postgresql_foundation (head)`. Repeating upgrade
was safe. `alembic check` returned exactly `No new upgrade operations detected.`
Startup performs no schema recreation. SQLite versions 1–5 are retained as legacy
provenance separately from Alembic history. Migration/import rollback was tested.

## 10. Authentication/security status

PASS: Argon2id PHC plus the preserved native Node hash encoding (64 MiB, 3 passes,
1 lane), generic login errors, SHA-256 opaque token storage, 8-hour expiry,
startup expiry cleanup, HttpOnly cookies, logout revocation and bounded throttle.
Production requires Secure cookies. Password hashes are excluded from responses
and OpenAPI. Exact configured CORS/Origin checks and a 1 MiB body limit passed.
Admin-only routes, PM project ownership, TL team ownership, PM-review/baseline
restrictions, cross-project match rejection and same-name actor-ID isolation passed.
Workflow/human/system audit rollback passed for submission, review, PM/team/TL
assignment, activity actions and edit, including a real PostgreSQL failing trigger.

## 11. Phase 7 intelligence regression

PASS: 253 pure-service golden/parity cases preserve extraction, matcher-v1,
confidence, evidence, Why Match / Why Not, ambiguity and deterministic outputs.
Live API and browser workflow: TL observation → extraction → 100% recommendation
→ PM review/evidence → confirm → actual 85% → TL feedback → Admin audit.
Live confirm/change/unmatch/reconfirm removes/recreates the correct contribution,
restores baseline plus unrelated contribution(s), and persists history/feedback.
Live edit reruns matching; ambiguous/unknown inputs do not approve themselves.
No LLM, embeddings, OCR, ASR or chatbot was added.

## 12. Tests

`node -v`: v24.21.0. `npm -v`: 11.19.0. Python: 3.12.14.
Actual `npm test`: **42 passed, 0 failed**, rerun after the final UI fix.
This includes the preserved 37 original reference regressions and five new
frontend API/selector tests. Intentional injected audit failures log error text
inside the reference suite; the rollback assertions passed.

## 13. Frontend build

Actual `npm run build`: PASS, rerun after the final responsive fix. Vite 8.3.1
transformed 1912 modules; output is under `frontend/dist` (ignored).
The actual `npm run dev` startup command was also verified separately.

## 14. Backend tests

Actual `python -m pytest backend/tests -q --tb=short -o cache_dir=.audit/pytest-cache`
with TEST_DATABASE_URL exported privately: **293 passed, 0 failed**.
Tests use real PostgreSQL/Alembic, isolated disposable schemas and no SQLite
replacement. One Starlette TestClient/httpx dependency deprecation warning remains.
`python -m pip check`: `No broken requirements found.`

## 15. Lint

Actual `npm run lint`: PASS, rerun after the final responsive fix.
`git diff --check`: PASS; Git's LF/CRLF notice is not a source error.
The initial cache-permission failure and corrective exclusion are disclosed below.

## 16. Browser verification

PASS using the Codex in-app browser against the isolated FastAPI/PostgreSQL
runtime: Home → Login → Admin, PM and TL, TL submission at 518px, PM evidence,
confirmation, linked schedule actual, TL feedback and Admin activity. Confirmed
85% actual and Reviewed state persisted. Logout returned to Home. Browser reload
after the real API restart preserved the authenticated Admin workspace. Console
warning/error query returned an empty list. Screenshot: `phase-7.1-pm-review.jpg`.
Live health, /docs and /openapi.json passed. Full live API confirmation/change/
unmatch/reconfirm/edit/ambiguity/logout passed; see `phase-7.1-runtime.json`.
Real Uvicorn process replacement preserved the exact scoped workspace and active
session over HTTP (reviews, actuals, contributions and feedback included).
Temporary audit browser tabs/viewport overrides and API/Vite processes were cleaned up.

## 17. Responsive verification

Home, Admin, PM and TL were checked at **1440, 1024, 768 and 518px**. At these
widths document widths were respectively 1431, 1015, 759 and 510: no page-wide
overflow. Screenshots inspected desktop/mobile PM review, mobile TL/Admin and
1024/768 Admin. Wide tables scroll inside their own containers.
Visual checks identified a clipped Home login control despite the document-width
check; that defect was fixed. Both existing login buttons now fit every width:
Management right edges 1385.4 / 982.7 / 734.9 / 493.3px respectively. Mobile PM
and TL login were repeated successfully after the fix. No UI redesign was made.

## 18. Files changed

Moved current React source/public/index into `frontend/`; moved original JS
services/data/backend tests into `tests/legacy/`; moved SQLite into legacy data.
Added FastAPI routes/config/security/contracts, pure Python services, SQLAlchemy
entities/repository/seed, Alembic migration, PostgreSQL pytest fixtures/tests,
requirements, env examples, import/seed/launcher scripts and audit evidence.
Updated package/workspace/lockfile, ESLint, gitignore, root/backend/database docs,
central frontend API client, TL selector import and Home header responsiveness.
Removed old Node application entrypoints/config/dev launcher; no second live
backend remains. A complete current change inventory accompanies this report.
Existing user changes were retained and compared against the saved current-state
archive, rather than replaced with the older Git HEAD.

## 19. SQLite migration/legacy status

PASS: the source was read-only, backed up with SQLite's online API, validated,
imported transactionally and checked for every value. Differences are zero:

| Source table | SQLite rows | PostgreSQL rows | Difference |
| --- | ---: | ---: | ---: |
| organizations | 1 | 1 | 0 |
| users | 13 | 13 | 0 |
| projects | 4 | 4 | 0 |
| project_manager_assignments | 1 | 1 | 0 |
| teams | 6 | 6 | 0 |
| schedule_activities | 10 | 10 | 0 |
| field_updates | 7 | 7 | 0 |
| activity_matches | 7 | 7 | 0 |
| reviews | 6 | 6 | 0 |
| review_history | 14 | 14 | 0 |
| schedule_activity_contributions | 1 | 1 | 0 |
| audit_events | 10 | 10 | 0 |
| sessions | 6 | 6 | 0 |
| schema_migrations | 5 | 5 | 0 |
| team_leader_assignments | 1 | 1 | 0 |

Team leader assignment is derived from the old teams relation. SQLite
schema_migrations maps to legacy_schema_migrations. Original hashes/sessions
are preserved; expired sessions remain expired. The source and both original/
import-specific backups are retained. See `sqlite-postgres-migration.json`.

### Failures found and fixes (not hidden)

| Exact failure / finding | Classification | Fix and rerun |
| --- | --- | --- |
| `pg_ctl: could not create restricted token: error code 87`; `could not start server: error code 3` | Environment | Approved local process startup; PostgreSQL accepted connections |
| Historical FieldUpdate.teamId was a required string although six seed records have null team IDs | Source code | Nullable response contract; seeded/history workspaces and API regressions passed |
| First pytest run: `10 failed, 282 passed`; examples `assert 403 == 500`, `assert 403 == 400`, schema tables `[]`, `DID NOT RAISE ValueError`, and `PostgreSQL target is not empty; import refused without changing existing data.` | Source/configuration | Removed public search-path fallback and corrected private TEST_DATABASE_URL. Added a missing-schema regression guard. See data recovery note below |
| Second pytest run: `assert 65 == 0`; `1 failed, 291 passed` | Test expectation | Rematch must retain the unrelated existing 65% contribution. Corrected expectation and asserted unrelated preservation; final 293 tests passed |
| `EPERM: operation not permitted, scandir 'D:\Coding\pravaha\.pytest_cache'` | Environment/configuration | Excluded generated pytest/Python caches from ESLint; lint passed |
| 518px Management button rectangle: left 868.66, right 1031.39, outside viewport | Source UI | Minimal Home header wrapping; right edge now 493.30 and mobile login passed |
| `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` | Dependency warning | Nonblocking warning retained as technical debt; all tests passed |
| Audit harness: `Relative module names not supported`; `Cannot find module ...frontend\node_modules\vite\bin\vite.js`; `relative path can't be expressed as a file URI` | Audit harness/environment | Used verified module/dependency paths and absolute source path; real startup/runtime/data checks rerun successfully |
| Screenshot save `EPERM: operation not permitted, open ...phase-7.1-pm-review.jpg` | Environment | Saved captured bytes through an approved single-request local artifact writer; verified JPG exists |

**Data recovery disclosure:** The initial private test URL mistakenly pointed to
the newly imported local PostgreSQL copy. Combined with public-schema fallback,
tests mutated that copy. The original SQLite and coherent pre-migration backup
were untouched. The affected PostgreSQL copy was retained for diagnostics, a new
canonical `pravaha_phase71` target was created, and all original data was imported
again from intact SQLite without resetting a database. Final tests used only the
dedicated test database; runtime/browser used only the separate runtime database.
A fresh independent comparison after all checks verified every original row,
value, hash, session, contribution and review/audit record in the canonical target.

## 20. Known technical debt

Per-process throttling needs shared storage before multiworker scaling. Snapshot
mutation locks serialize organization writes; collections/audit exposure are not
fully paginated (audit loader limits 500). JSONB retains legacy presentation
contracts; historic null team/actor associations remain preserved. Baseline editing
is intentionally not implemented (501). Some dashboard charts/metrics remain
explicitly illustrative. Attachment names are metadata only. Starlette/httpx test
client dependency warning remains. Portable PostgreSQL and private diagnostic
copies are local audit artifacts, not committed deployment infrastructure.

## 21. Anything NOT verified

No real Neon account/network connection, cloud deployment, production HTTPS cookie
flow, multiworker throttling, load/performance test, or provider backup restore was
performed. These are future operations, outside Phase 7.1; compatible URL/env and
production-cookie configuration paths are tested. All required local migrations,
PostgreSQL regressions, commands, HTTP/browser workflow and responsive widths passed.
Phase 8 has not started.

PHASE 7.1 COMPLETE - PHASE 8 NOT STARTED
