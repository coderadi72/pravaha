# PRAVAHA - Phase 12 project intelligence assistant

SIH26122 · Oil India Limited · project progress monitoring prototype.
The existing role hierarchy and workflow are preserved. Phase 8 adds backend-generated execution intelligence, explainable warnings, schedule variance and persisted institutional memory. Phase 9 extends this baseline with schedule imports, versions, typed dependencies, safe attachments, scoped search and operational controls.

Current work: **Phase 12**. Approved order: **12 → 13 → 14 → 11 → 15**;
Phase 11 is deferred. Phase 12 adds a read-only project assistant and animated
robot to existing Admin, PM and TL dashboards. It does not change matching,
PM confirmation, accepted actuals or operational records. See the
[Phase 12 blueprint](docs/phase-12-blueprint.md) and
[verification report](docs/phase-12-verification.md). Live Groq/NVIDIA checks are
pending credentials; **PHASE 12 NOT COMPLETE** until real operation is verified.

## Architecture

```text
React / Vite (frontend/)
    → centralized environment-configured API client
FastAPI / Pydantic (backend/app/api/)
    → authentication, permissions and workflow services
    → deterministic extraction / matching / confidence / evidence
SQLAlchemy 2.x repositories
    → PostgreSQL (local or a compatible Neon DATABASE_URL)
Alembic → incremental database migrations
```

The intended deployment path is Vercel for the frontend, Render's native
Python service for FastAPI, and Neon PostgreSQL for the database. Provider
deployment and provider-level recovery checks are operational deployment work;
the repository does not claim that they have been executed.

FastAPI is the single application API. SQLite and the old Node implementation
are retained exclusively for migration and regression references under
`database/legacy/` and `tests/legacy/`; neither is a production entry point.

```text
frontend/             React source, public assets, Vite configuration, package
backend/app/          API, core configuration/security, models, schemas, services, db
backend/alembic/      Frozen schema revisions and migration environment
backend/tests/        pytest configuration, security, PostgreSQL/API and parity tests
database/seed/        Clearly labeled Phase 7 demonstration dataset
database/legacy/      Ignored SQLite migration inputs and backups
docs/                 Architecture audit, migration report and final verification
scripts/              API launcher, explicit seed, one-way SQLite importer
tests/                Frontend client tests and isolated legacy regression reference
```

## Requirements and install

Node **24.7+** (native Argon2 and SQLite are needed by legacy regression tests),
npm, Python **3.11+**, and a running PostgreSQL instance. This audit used Node
24.21.0, npm 11.19.0, Python 3.12.14 and PostgreSQL 18.6.
Run these commands from the repository root:

```powershell
npm install
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
```

On POSIX activate with `source .venv/bin/activate`. The backend also accepts
`backend/.env` if you prefer a separate backend file. Actual env files, secrets,
venvs, databases, caches, builds and logs are ignored; examples remain shareable.

## Database setup and migrations

Create an empty application database owned by a non-superuser application role
using your PostgreSQL administrator or provider console. Set `DATABASE_URL` to
that database. No source file contains database credentials. For example, the
connection shape is `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE`.
URL-encode special characters in URL credentials.

```powershell
python -m alembic -c backend/alembic.ini upgrade head
python -m alembic -c backend/alembic.ini current
```

Startup never creates, drops or resets tables. The initial PostgreSQL revision
is `0002_execution_warnings` (following `0001_postgresql_foundation`); subsequent schema changes need new incremental
revisions. Foreign keys, primary keys, unique email/assignment constraints,
indexes, role checks, JSONB and timezone-aware timestamps preserve the workflow.
`DB_SCHEMA` selects one schema strictly; a missing schema must fail rather than
fall through to another schema. Organizations are locked before snapshot writes.
Workflow, authenticated user audit and system matcher audit commit together.

### Existing SQLite data

**Import existing data OR seed a new demo database.** Do not seed before importing.
Keep a backup before migrating. See [database guide](database/README.md).

```powershell
python -m scripts.migrate_sqlite --source database/legacy/pravaha.sqlite --report docs/sqlite-postgres-migration.json
```

The importer opens SQLite read-only, creates a coherent online backup (including
committed WAL pages), validates integrity/FKs, refuses a populated PostgreSQL
target, and imports in one transaction. IDs, JSON payloads, baselines,
contributions, hashes, sessions, review/audit history and assignments survive.
It verifies row counts and every imported value. SQLite migration versions 1–5
are preserved in `legacy_schema_migrations`; Alembic owns PostgreSQL history.
Leader assignment rows derive from the old team relation.
Do not copy a live SQLite main file alone: use its backup API or retain its WAL
and SHM files with a coherent stopped database. SQLite is never opened by API runtime.
For PostgreSQL use normal `pg_dump`/provider backups, and keep credentials out of
command history/logs. The temporary local audit server/tools are ignored machine
artifacts; PostgreSQL must be running before starting PRAVAHA.

### New demonstration database

Set all six `SEED_ADMIN_EMAIL/PASSWORD`, `SEED_PM_EMAIL/PASSWORD`, and
`SEED_TL_EMAIL/PASSWORD` values privately. Passwords must be 12–128 characters
with uppercase, lowercase, digit and special character. Examples have **blank
passwords**, and missing/invalid credentials fail before writes.

```powershell
python -m scripts.seed
```

Only ADMIN-001, PM-001 and TL-001 are enabled by the demo seed. Disabled PM/TL
records have no operational assignments. Seed is transactional and skips a
populated organization without overwriting it. Login with your configured email
and password; there are no default application passwords. Existing imported
accounts retain their original passwords.

## Environment configuration

Backend precedence: process env → `backend/.env` → root `.env` → safe defaults.
Frontend precedence: process env → frontend mode env files → root mode env files.
Restart Vite / rebuild the frontend when changing `VITE_*` build configuration.
Never put secrets in `VITE_*`; these values are public in browser bundles.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Required PostgreSQL URL; `postgres://` and `postgresql://` normalize to psycopg |
| `DB_SCHEMA` | Strict schema selection; default `public` |
| `APP_ENV` | `development`, `test`, or `production` |
| `API_HOST`, `API_PORT` | Backend bind address / port; examples 127.0.0.1 / 8000 |
| `CORS_ORIGINS` | Comma-separated exact frontend origins; credentials allowed only for configured origins |
| `VITE_API_BASE_URL` | Required full API base, e.g. `http://127.0.0.1:8000/api`, or a same-origin `/api` proxy |
| `VITE_ATTACHMENT_MAX_BYTES` | Public frontend upload limit in bytes; must match the backend attachment limit |
| `VITE_HOST`, `VITE_PORT` | Required Vite bind settings; examples 127.0.0.1 / 5173 |
| `SESSION_COOKIE_SECURE` | Defaults true in production; false production configuration rejected |
| `SESSION_COOKIE_SAMESITE` | `lax` default; cross-site HTTPS deployments require `none` and Secure |
| `ENABLE_API_DOCS` | Defaults enabled in development, disabled in production |
| `SQL_ECHO` | Off by default; enabling SQL logging may expose bound application data |
| `TEST_DATABASE_URL` | Dedicated test PostgreSQL connection; export into the pytest process |
| `SEED_*` | Explicit demo credential configuration only |
| `JWT_SECRET`, `SESSION_SECRET` | Reserved example placeholders; unused because opaque DB-backed sessions are canonical |
| `LOGIN_MAX_ATTEMPTS`, `LOGIN_WINDOW_SECONDS`, `LOGIN_MAX_BUCKETS` | Shared login throttling bounds |
| `SESSION_TTL_SECONDS` | Opaque session lifetime |
| `REQUEST_BODY_LIMIT_BYTES`, `REQUEST_UPLOAD_BODY_LIMIT_BYTES` | Request body bounds |
| `ATTACHMENT_MAX_BYTES`, `IMAGE_MAX_PIXELS` | Attachment and image validation bounds |
| `XLSX_MAX_ENTRIES`, `XLSX_MAX_UNCOMPRESSED_BYTES`, `XLSX_MAX_COMPRESSION_RATIO` | XLSX archive safety bounds |
| `SCHEDULE_MAX_ROWS`, `SCHEDULE_MAX_COLUMNS`, `SCHEDULE_MAX_RELATIONSHIPS` | Schedule import bounds |
| `DEPENDENCY_CELL_MAX_COUNT`, `DEPENDENCY_MAX_LAG_DAYS`, `INTELLIGENCE_MAX_INPUT_ROWS` | Dependency and intelligence capacity bounds |

## Phase 12 assistant setup

For the targeted provider/UI correction and current evidence, see
[Project Assistant fix verification](docs/project-assistant-fix-verification.md)
and [conversation and mini-pet verification](docs/project-assistant-conversation-verification.md).

Keep secrets in `backend/.env` or the backend hosting environment. Never place
provider keys in frontend files, `VITE_*`, committed files or chat. For hosted
inference set these values privately:

```dotenv
AI_PROVIDER=auto
AI_PROVIDER_ORDER=groq,nvidia
GROQ_API_KEY=<your Groq key>
GROQ_MODEL=openai/gpt-oss-20b
GROQ_REASONING_EFFORT=low
NVIDIA_API_KEY=<your NVIDIA hosted NIM key>
NVIDIA_MODEL=z-ai/glm-5.3-flash
NVIDIA_REASONING_EFFORT=low
AI_RESPONSE_FORMAT=json_object
AI_FALLBACK_ENABLED=true
```

Only one key is necessary to configure one provider. Both are needed to verify
both adapters and use failover. Select a model available to your account;
model access and multilingual output are not established by configuration.
The NVIDIA example uses the full hosted model ID, not the shorter Build page
label. GLM always reasons; its conversation setting clears old thinking, and
the transport omits unsupported JSON response-format flags for this model.
Provider base URLs default to `https://api.groq.com/openai/v1` and
`https://integrate.api.nvidia.com/v1`; these are operator settings, never
model-supplied URLs. This uses NVIDIA's hosted API, with no local inference
service or Docker requirement.

`AI_PROVIDER=none` explicitly disables external calls even when keys exist.
`auto` tries configured provider-specific keys in `AI_PROVIDER_ORDER`.
Explicit `groq`/`nvidia` selects that primary, followed by the other configured
providers in `AI_PROVIDER_ORDER`. Its nonempty specific key
takes precedence over `AI_API_KEY`; explicitly set specific model/base values
take precedence over generic `AI_MODEL`/`AI_BASE_URL`. Generic values are
ignored in auto mode. Missing keys and provider failure use visibly labelled
guided fallback when enabled after configured attempts fail. Greetings, casual
conversation, project paraphrases, follow-ups and supported workflow help use
the provider with authorized context. Private-information requests and unrelated
questions are refused or redirected locally before inference.
Fallback draws current authorized data; it does not imitate model reasoning.

All assistant bounds are listed in root/backend `.env.example`:

| Configuration | Default / purpose |
| --- | --- |
| `AI_DEFAULT_LANGUAGE`, `AI_SUPPORTED_LANGUAGES` | `en`; `en,hi,hi-Latn` catalogues |
| `AI_REQUEST_TIMEOUT_SECONDS`, `AI_MAX_RETRIES` | 30 seconds per attempt; 0 retries by default, then available secondary |
| `AI_MAX_TOOL_CALLS`, `ASSISTANT_RECORD_LIMIT` | 3 read tools; 12 records per page |
| `AI_MAX_CONTEXT_CHARS`, `ASSISTANT_EXCERPT_CHARS` | 24,000 context characters; 300 per excerpt |
| `AI_MAX_INPUT_TOKENS` | 3,000 conservative UTF-8 byte plus framing upper bound, including instructions, question, history and projected evidence; not a provider usage measurement |
| `AI_MAX_OUTPUT_TOKENS`, `NVIDIA_MAX_OUTPUT_TOKENS` | 500 requested; NVIDIA also obeys its configured cap (4,096) |
| `GROQ_REASONING_EFFORT` | Optional `low/medium/high` for GPT-OSS; example uses `low` |
| `NVIDIA_REASONING_EFFORT` | Optional `none/low/high/max`; model-specific settings only. Nemotron `none` disables thinking; GLM uses effort and clears old thinking, and cannot disable it. |
| `AI_RESPONSE_FORMAT` | `text` by default; the example enables supported JSON object mode. Schema and evidence validation always remain mandatory. |
| `AI_MAX_RESPONSE_BYTES`, `ASSISTANT_QUESTION_CHARS` | 131,072 response bytes; 1,200 question characters |
| `AI_COOLDOWN_SECONDS` | 60 seconds unless the provider supplies actual Retry-After |
| `AI_DAILY_REQUEST_BUDGET` | 0 disables application budget; positive bound counts attempted provider requests per worker per UTC day |
| `ASSISTANT_MAX_REQUESTS`, `ASSISTANT_WINDOW_SECONDS` | 4 requests per user per 60 seconds, including local safety responses |
| `ASSISTANT_MAX_REQUESTS_PER_SESSION` | 20 inference attempts per authenticated login session; shared PostgreSQL storage, survives reset/restart |
| `ASSISTANT_MAX_CONCURRENT` | 2 in-flight requests per worker |
| `ASSISTANT_HISTORY_QUESTIONS`, `ASSISTANT_CONVERSATION_TTL_SECONDS` | Up to 8 signed conversation messages; 1,800-second token lifetime; oldest history removed first to fit input budget |

Provider retry/context reduction and failover are bounded. Cancellation closes
the transport and prevents another provider call. Budget/cooldown/concurrency
are per worker and reset on restart, except the shared PostgreSQL user/session
budgets; they are not a distributed billing cap. Assistant throttling always
uses the existing PostgreSQL rate-limit table, even when local login throttling
uses memory. A new conversation does not replenish the session budget. Limits
are PRAVAHA safeguards, not advertised free-tier quotas.

English, Hindi and Hinglish follow each new message; ambiguous short follow-ups
retain the previous language. The dropdown supplies a preference, not a forced
language override. Actual record names, IDs, dates,
numbers and source data remain unchanged. Live AI multilingual quality requires
separate checks. Questions outside PRAVAHA receive a scope reminder.

When enabled, the selected provider receives the sanitized question, bounded
conversation messages and projected authorized execution evidence. Old answers
are conversation context, not current project facts. Confidential HR
tables, credentials, account rosters and private provisioning exports are not
retrieved. Free-text redaction is defensive and heuristic; operators must not
put confidential personal content into execution descriptions or questions.
Provider retention and account policies remain an operator responsibility.
Interpretation is advisory and cannot approve progress or modify any record.

### Assistant API

| Endpoint | Contract |
| --- | --- |
| `GET /api/assistant/contexts?limit=50&offset=0` | Current authorized projects, role, enabled languages and configuration-only provider status; maximum page 100 |
| `POST /api/assistant/ask` | `question`, optional `project_id`, `activity_id`, `intent`, `language` (`auto/en/hi/hi-Latn`) and signed `conversation`; all extra fields rejected |
| `GET /api/assistant/source?reference=...` | Server-issued signed evidence reference; fresh session/assignment checks and current source reread |

Responses label `AI`, `GUIDED_FALLBACK` or local `GUIDANCE`, include interpretation/uncertainty,
retrieval timestamps, partial-result indicators and authorized evidence.
Source links are generated by the server, never the model. Every read and the
final response recheck persisted permissions. Sources are current rereads,
not immutable copies of an older answer. Project/session/reassignment changes
invalidate signed conversation/source context. No conversation rows or domain
writes are made; browser history is memory-only. The session budget writes only
to the existing rate-limit table. Worker and Department roles
are denied; TL reads are filtered to its team before calculation and do not
open the existing Admin/PM intelligence API.

Restart the backend after local `.env` changes. Set Render secrets through its
environment configuration. Rebuild Vercel after public frontend environment
changes; set `VITE_API_BASE_URL` to the Render API. Preserve exact HTTPS CORS
origins, secure cookies (`SameSite=none` when cross-site), production database
SSL and PostgreSQL throttling. The compact inline SVG assistant mark and lazy widget bundle use
the existing `/assets/` rewrite exclusion; no temporary reference file is used.
Actual Vercel/Render/Neon deployment has not been claimed.

Verification commands:

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_phase12
npm test
npm run lint
npm run build
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\alembic.exe -c backend/alembic.ini check
.\.venv\Scripts\alembic.exe -c backend/alembic.ini current
```

## Local development

With PostgreSQL running, migrations applied and the Python venv activated:

```powershell
# Terminal 1: configuration-driven FastAPI/Uvicorn
npm run server
# alternatively: python scripts/run_backend.py --reload

# Terminal 2: frontend only
npm run dev
```

Defaults in the examples: frontend `http://127.0.0.1:5173`, backend
`http://127.0.0.1:8000`, health `/api/health`, interactive docs `/docs` and schema
`/openapi.json` on the backend. Use the same hostname on both sides for local
SameSite cookies and include the frontend origin in `CORS_ORIGINS`.
There is no Node API proxy competing with FastAPI.
`npm start` runs the backend without reload; `npm run preview` serves the frontend build.

## API overview

All contracts are explicit Pydantic request/response models, retaining the
existing camelCase frontend shape. Errors use `{error:{code,message}}`.
Protected endpoints use the HttpOnly `pravaha_session` cookie.

| Method / path | Access / purpose |
| --- | --- |
| `GET /api/health` | Public health and safe database connectivity check |
| `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` | Sign in, revoke session, session identity |
| `POST /api/auth/signup` | Public official-domain registration request; pending approval, no session |
| `GET /api/admin/registrations` | Admin-only organization-scoped requests, status filter and pagination |
| `POST /api/admin/registrations/{id}/approve`, `/reject` | Admin approves an eligible role or rejects the request |
| `GET /api/workspace`, `GET /api/projects` | Authenticated scoped data |
| `GET /api/projects/{id}` | Admin or assigned PM |
| `GET /api/projects/{id}/schedule`, `/field-updates`, `/reviews` | Admin or assigned PM |
| `GET /api/admin/organization`, `/projects`, `/users`, `/teams` | Admin-only organization resources and activity |
| `POST /api/admin/users` | Admin provisions PM/TL credentials |
| `PATCH /api/admin/projects/{id}/manager` | Admin assigns/clears enabled PM |
| `PATCH /api/admin/teams/{id}/assignment`, `/leader` | Admin team/project and enabled TL assignment |
| `GET /api/team-leader/me`, `/activities`, `/field-updates` | TL's own team and project |
| `POST /api/team-leader/field-updates` | TL observation and deterministic intelligence |
| `PATCH /api/team-leader/field-updates/{id}` | Pending own update edit, rematch, reconciliation and review reset |
| `POST /api/team-leader/activities/{id}/actions` | Own assigned activity start/update/complete/block |
| `POST /api/reviews/{updateId}/{decision}` | Assigned PM: confirm/change-match/unmatch/request-info/request-review |
| `PATCH /api/projects/{id}/schedule/{activityId}/baseline` | Authorization preserved; baseline editing remains 501 / not implemented |

Ownership is enforced server-side by authenticated IDs, organization/project/
team relationships and submitter IDs. Same-name accounts cannot bypass it.
TL responses redact out-of-team candidates, baselines and system recommendations.

### Official-domain registration and approval

Apply the additive Alembic revision `0005_registration_requests` with
`python -m alembic -c backend/alembic.ini upgrade head`. It creates the pending
request table and indexes without changing existing users, passwords, or sessions.

Signup accepts `{name,email,password,confirmPassword,roleCategory}`. The only
categories are `MANAGEMENT` and `SUPERVISOR`. The backend parses the complete
normalized email domain and requires `pravaha.management.com` or
`pravaha.supervisor.com`, respectively; suffixes, lookalikes, mismatched categories,
and malformed addresses are rejected. Passwords use the existing 12–128 character
policy and Argon2id. Pending requests create no active user or session. New and
duplicate submissions return the same HTTP 202 response without an identifier,
preventing the public endpoint from revealing account existence.

The Admin **Registrations** view supports pending, approved, and rejected requests.
Approval associates the account with the reviewing Admin's organization, activates
it, and preserves the existing login/session flow. Management approval permits
only the existing `PROJECT_MANAGER` or `DEPARTMENT` roles; Supervisor approval
permits only `TEAM_LEADER`. Public signup never creates an Admin. Project/team
assignments remain separate authorized Admin actions. Rejection creates no account.
Review and audit writes commit together; terminal requests no longer retain a
password hash after transfer or rejection.

`REGISTRATION_REVIEW_ORGANIZATION_ID` selects the review organization server-side.
An existing database with exactly one organization can resolve it automatically;
multiple organizations require explicit operator configuration. Users cannot
choose or override the organization. Each Admin sees only their organization's
requests. `SIGNUP_MAX_ATTEMPTS`, `SIGNUP_WINDOW_SECONDS`, and `SIGNUP_MAX_BUCKETS`
configure the independent public registration throttle using the existing limiter.

These rules validate the configured domain strings. They do not verify email
ownership, DNS ownership, or enterprise domain ownership. Google/GitHub buttons
retain their current UI behavior; OAuth integration is deferred.

## Phase 7 intelligence and security

Pure Python services preserve deterministic extraction, L5/L6 candidate scoring,
confidence bands, evidence, Why Match / Why Not and ambiguity handling. Golden
fixtures compare the original JS outputs and generated wording variations.
Recommendations never approve themselves. PM confirm/change/unmatch/reconfirm
reconciles contribution removal/addition, restores baseline plus unrelated
contributions, retains review history and feedback, and records actor IDs.
Free-text submission waits for PM confirmation; explicit assigned-activity
execution actions retain the existing field-reported actuals behavior.
No LLM, embedding service, OCR, ASR, chatbot or additional worker role is introduced.
Attachments remain filename metadata, with no extraction/upload pipeline.

Argon2id hashes use 64 MiB memory, three iterations and one parallel lane.
The preserved native Node encoding and standard PHC hashes are both verified
without password reset. Password hashes never appear in response data.
Opaque 32-byte tokens are stored only as SHA-256 hashes, expire after eight hours,
and are revoked on logout. Login errors are generic; five failures trigger a
15-minute bounded per-process throttle. Request bodies are capped at 1 MiB and
mutating browser requests require an allowed Origin. Production cookies are Secure.

## Verification

```powershell
node -v
npm -v
npm test
npm run lint
npm run build
# Dedicated test DB whose owner may create isolated schemas:
$env:TEST_DATABASE_URL = 'YOUR_DEDICATED_POSTGRESQL_TEST_URL'
python -m pytest backend/tests -q
```

`npm test` preserves 37 original JS regression tests and adds five frontend
configuration/client tests. Backend pytest uses genuine PostgreSQL and Alembic
in a unique disposable schema per database/API test. The schema search path has
no public fallback. Pure-service tests can run separately with
`python -m pytest backend/tests/test_intelligence.py -q`.
Tests inject human/system audit failures and verify workflow rollback.
See `docs/phase-7.1-audit.md` for actual commands/results, runtime/browser checks,
responsive checks, migration counts, fixes and limitations.

## Future deployment / known limitations

No deployment was performed. A compatible Neon URL (including `sslmode=require`)
can replace `DATABASE_URL`; the app source stays unchanged. Run Alembic against
the new target and configure the backend bind/port, frontend API URL, exact CORS
origins, HTTPS cookie policy and provider backups. The frontend API URL is set
at build time, so rebuild when changing it. Hosting-specific commands/config are
infrastructure choices; `uvicorn backend.app.main:app --host ... --port ...` is
also available when a platform supplies its port outside the launcher.

Development and test defaults use the bounded in-process limiter; production
requires `RATE_LIMIT_BACKEND=postgresql` for shared limiting across workers.
Organization locks serialize snapshot writes, collection APIs remain unpaginated,
and JSONB payloads retain the legacy presentation shape. The public landing page
retains clearly labeled illustrative demo material; authenticated PM/Admin
execution analytics use backend results. Auth uses opaque sessions, not JWT.
The target Vercel -> Render -> Neon deployment and provider operations remain
future deployment validation, while the repository implementation and Phase 9
verification are complete.
The pinned Starlette TestClient emits an httpx deprecation warning; tests still pass.
See `docs/phase-9-production-verification.md` for the final Phase 9 gate.


## Phase 8 execution intelligence

The backend calculates calendar-day start/finish/duration variance from persisted
PM-reviewed matches and their contributions. TL provisional actions remain visible
in the original reporting workflow but are excluded from confirmed intelligence.
Missing or invalid actual evidence is `UNKNOWN` / `null`, displayed as N/A.
Completion may be confirmed by 100% progress without inventing a finish date.
There is no weighted overall project percentage, productivity estimate or causal prediction.

New authenticated APIs (Admin within its organization, PM only assigned projects;
TL denied on all these endpoints):

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/intelligence/projects` | Paginated permitted project list |
| GET | `/api/intelligence/portfolio` | Batched portfolio health, summary and coverage |
| GET | `/api/intelligence/projects/{project_id}` | Current execution summary, variance, warnings, data health |
| POST | `/api/intelligence/projects/{project_id}/refresh` | Persist meaningful warning/health changes and audit |
| PATCH | `/api/intelligence/projects/{project_id}/warnings/{warning_id}/acknowledge` | Record authenticated acknowledgement |
| GET | `/api/intelligence/projects/{project_id}/memory` | Search/filter project or activity records |

Project lists, summary activity/warning pages and memory accept `limit` (1–100,
default 50) and nonnegative `offset`; portfolio uses 1–20/default 20. Summary pages
have separate `activityTotal` and `warningTotal`. Memory also accepts `q` (literal,
case-insensitive, maximum 200 characters), `activity_id`, and `kind`:
`field_update`, `review_history`, `review`, `confirmed_actual`, `audit`.
An activity filter must belong to the authorized project. Reads never mutate data.

Warning IDs are stable per project/activity/type/update. Lifecycle is OPEN →
ACKNOWLEDGED → RESOLVED; a recurring resolved condition reopens its stable ID.
Acknowledgement is attention tracking, not suppression or PM confirmation.
Field submission/edit, activity action and PM review reconcile warnings and project
intelligence in their existing transaction. Workflow, warning and audit failures
roll back together. Explicit refresh also captures date-dependent changes.
No background scheduler or duplicate event ledger was introduced.

Rules and configurable defaults (`.env.example`):

- `INTELLIGENCE_STALE_DAYS=7`: latest linked report, or planned start if none; completed/future activities excluded.
- `INTELLIGENCE_FINISH_WINDOW_DAYS=3`: upcoming planned finish window.
- `INTELLIGENCE_MIN_PROGRESS=80`: approaching-finish confirmed progress threshold; absent progress is an evidence gap.
- `INTELLIGENCE_HIGH_DELAY_DAYS=7`: HIGH confirmed adverse date variance/finish overrun; smaller positive signals MEDIUM.
- `INTELLIGENCE_INCOMPLETE_THRESHOLD=3`: linked reports missing activity, discipline or location produce MEDIUM attention.
- Unmatched updates and basic data issues LOW; pending review/staleness MEDIUM; invalid cross-project linkage and potential dependency exposure HIGH. No CRITICAL is generated.

Linkage coverage = 100 × valid proposed/accepted linked updates / all relevant
project updates. Data coverage = 100 × activities with linked reports / scheduled
activities. Duplicate IDs count once; denominator zero returns null/N/A.
Summary completion/variance uses confirmed evidence, independently of coverage.
Health dimensions include schedule, execution, capture, linkage, review, dependency
exposure and warning level; each has a reason, with no decorative combined score.

No dependency graph exists in the current canonical schedule. UI therefore shows
UNAVAILABLE. The engine supports explicitly persisted `predecessorIds` (internal
activity IDs, finish-to-start). It subtracts nonnegative planned slack from confirmed
finish delay or incomplete confirmed finish overrun. It does not infer relations,
propagate late starts into definite finish delays or predict a critical path.

Institutional memory reuses PostgreSQL field reports, reviews/history, contributions
and audit events. Warning transitions and intelligence snapshots record previous/new
values and evidence in the same audit ledger. Review audits retain former schedule
links so an activity's historical reports survive rematching/unmatching. Timestamp
ordering uses PostgreSQL timestamps; undated review records remain undated.
Phase 7 `MatchEvidencePanel` and Why Not explanations are reused.

Inputs are project-scoped and capped at 10,000 rows per input collection (also per
portfolio batch). Exceeding capacity returns a structured 409 instead of silently
truncating calculations. Portfolio fetches are batched without one query per project;
memory pagination/filtering occurs in SQL. Larger deployments need aggregate/query
and search-index work, plus the existing snapshot-write scalability improvements.

Verification evidence and limitations: `docs/phase-8-audit.md`,
`docs/phase-8-migration.json`, `docs/phase-8-runtime.json`,
`docs/phase-8-consistency.json`, `docs/phase-8-responsive.json`.
No Neon/cloud/HTTPS deployment, multiple-worker behavior or production load test
was performed. This remains a locally verified prototype.


## Phase 9 ingestion and operational APIs

PostgreSQL remains authoritative. Incremental Alembic revision `0003_schedule_ingestion` adds schedule versions, typed dependency relationships, attachments and shared login buckets without resetting previous data.
Run `alembic -c backend/alembic.ini upgrade head` before starting the API. Startup validates the migration head.

| Endpoint | Access / purpose |
| --- | --- |
| `GET /api/ready` | Minimal DB and migration readiness |
| `GET /api/admin/system` | Admin safe system/provider/backup status |
| `POST /api/admin/projects` | Admin creates project; assignment remains separate |
| `POST /api/projects/{id}/imports/preview` | Admin/assigned PM validates CSV/XLSX with column mapping |
| `POST /api/projects/{id}/imports/commit` | Same access; exact preview checksum and expected current version required |
| `GET /api/projects/{id}/schedule-versions?limit=50&offset=0` | Scoped immutable version metadata |
| `POST /api/projects/{id}/schedule-versions/compare?before_id=...&after_id=...` | Scoped audited comparison |
| `GET /api/projects/{id}/dependencies` | Admin/assigned PM; current persisted graph |
| `POST /api/field-updates/{id}/attachments` | Reporting TL only; upload JSON filename/contentBase64 |
| `GET /api/field-updates/{id}/attachments?limit=50&offset=0` | Scoped metadata; TL owns report |
| `GET /api/attachments/{id}` | Authorized attachment download, never public |
| `POST /api/attachments/{id}/process` | Scoped audited OCR/ASR/advanced request; honest unavailable fallback |
| `GET /api/search?q=...&kind=all&limit=20&offset=0` | SQL filtering with role/project/team scope |

Import body: `filename`, `contentBase64`, optional `mapping` (source header to supported field). Commit adds `previewChecksum` and `expectedVersionId` returned by preview. No safe partial imports: all validation errors block commit.
Required fields: activityId, activityName, plannedStart, plannedEnd. Dates are ISO YYYY-MM-DD or native Excel dates; progress 0–100. Dependencies use comma-separated `ActivityID:FS:lagDays`; FS/SS/FF/SF supported, cycles and absent activities rejected.
Limits: 5 MiB file, 2,000 activities, 60 columns, 10,000 relationships. One XLSX worksheet; formula cells, macros and external links rejected. Unsupported columns remain in version `extraColumns`.
Existing actuals/contributions/baselines/history remain; removed activities are retired rather than deleted. New imported actuals are labeled schedule_import; PM confirmed contributions take precedence.
TL text requests also accept quantity/unit/remarks/blocker/crew/equipment. Attachment upload follows text submission as a separate transaction: if upload fails, the saved observation remains and the UI reports that explicitly.
CSV/XLSX/PDF/PNG/JPEG/TXT/WAV uploads are validated by bytes and served as downloads. Voice/OCR/advanced AI adapters are NOT IMPLEMENTED; defaults return NOT_CONFIGURED, configured names return UNAVAILABLE. Existing deterministic matching is unchanged.
Negative float is used only when supplied by the schedule. Dependency exposure is an explainable estimate with depth/type/lag/evidence; no forecast dates or critical path are invented.
See [deployment and recovery](docs/phase-9-deployment.md) and [Phase 9 audit](docs/phase-9-audit.md) for verification evidence and known limits.

## Phase 10 organization workflows

**PHASE 10 COMPLETE.** Phases 11–15 have not been implemented.

See the [organization blueprint, relationships and permission matrix](docs/phase-10-blueprint.md)
and [Phase 10 verification report](docs/phase-10-verification.md). Phase 10 adds
24 departments, units, locations, designations, employees, reporting lines,
skills, project membership and participating departments. Employee identity,
designation and account permissions are separate. React Router retains Admin
section navigation; existing PM/TL execution dashboards include scoped support
workflows.

The Admin console covers overview, projects, PMs, teams, workers, assignments,
departments, imports, reports, activity, audit and settings. Business, Materials,
People, Quality and HSE use connected records and explicit status actions.
Assignments require **Save assignment**. Selecting an account/team/project never
reassigns ownership by itself. Allocations validate active entities, enabled
PM/TL ownership, effective dates and a single active allocation. Transfers retain
history; teams containing historical execution links cannot be moved between
projects. Former TLs retain read access to their own submissions; current owning
PM/Admin retain project history.

Department accounts need explicit module grants. Confidential performance,
employee-relations, grievance and wellbeing cases require `hr-confidential`,
including for Admin. Ordinary Admin/PM summaries exclude private case records.
WORKFORCE accounts can authenticate, inspect their own safe session identity and
log out. They have no management API permissions and receive a generic access
restriction, with no Worker dashboard. Earlier phase role descriptions refer to
the role model at that phase; Phase 10 introduces these two least-privilege roles.

### Migration and provisioning

Apply the frozen incremental `0004_organization` revision after `0003`:

```powershell
.\.venv\Scripts\alembic.exe -c backend/alembic.ini upgrade head
.\.venv\Scripts\alembic.exe -c backend/alembic.ini check
```

Existing tables are retained. The migration verification compared all 20
pre-existing tables before/after and found no changed rows; the added nullable
login-ID column is excluded from the old-user projection comparison. PostgreSQL
remains the persisted source of truth. Do not reset the database or reseed it to
apply this migration.

An operator with trusted local database access and an enabled Admin account may
provision an isolated synthetic organization:

```powershell
.\.venv\Scripts\python.exe -m scripts.generate_phase10_demo --admin-id ADMIN-001 --namespace phase10
```

Default: **20 PMs × 8 teams × 20 workers = 3,200 workers**, 160 TLs, 20 projects,
160 teams, 3,386 employees/accounts and 24 departments. Supporting examples
include commercial traceability, procurement/stock/site issue, all eight People
record kinds, inspection/NCR and safety corrective actions. Information is
labelled Demo Data and is not operational Oil India data.

Options: `--pms` (1–25), `--teams-per-pm` (1–9), `--workers-per-team` (1–30).
Rerunning the same namespace/dimensions does not overwrite accounts, regenerate
passwords or duplicate allocations. Different dimensions for an existing namespace
are rejected. Lists use SQL search and pagination (default 25, maximum 100).

Every generated worker has a realistic name, stable workforce identifier,
department/discipline/skill links, unique login ID and individual random initial
password. Only Argon2id hashes persist in PostgreSQL. The one-time plaintext
demo export is `.audit/provisioning/<namespace>-credentials.json`, restricted to
the operator (Windows ACL or Unix private permissions), excluded from Git and
outside all public paths. Retrieve it locally as that operator and keep it
private. APIs cannot retrieve passwords or hashes. Provisioning audit records
contain totals and identifiers, never secrets. Reruns do not re-export credentials.

### Organization and module API overview

| Endpoint | Purpose / access |
| --- | --- |
| `GET /api/organization/context` | Safe resource metadata and current capabilities; Worker denied |
| `GET /api/organization/overview` | Admin persisted counts and attention items |
| `GET /api/organization/analytics` | Admin-only, organization-scoped dashboard aggregates from existing execution intelligence; bounded inputs |
| `GET /api/organization/roster?q=&limit=25&offset=0` | Admin roster; PM/TL active project/team workforce; authorized People staff |
| `GET /api/organization/lookups/{projects,teams,accounts}` | Scoped searchable selectors; accounts Admin-only |
| `POST /api/organization/teams` | Admin creates a team linked to an active project |
| `POST /api/organization/allocations` | Admin explicit allocation/transfer (`employee_id`, `project_id`, `team_id`, `effective_start`, `transfer`) |
| `GET /api/organization/allocations/{employee_id}` | Admin allocation history |
| `POST /api/organization/allocations/{id}/end` | Admin closes allocation with `effective_end` |
| `GET /api/organization/memberships/{project_id}` / `POST /api/organization/memberships` | Admin project members or participating departments |
| `POST /api/organization/skills` | Admin employee/skill link |
| `GET/POST /api/organization/grants` | Admin explicit responsibility grants/revocation |
| `GET /api/organization/stock` | Admin/materials responsibility; SQL-grouped inventory balances |
| `GET/POST /api/modules/{resource}` | Scoped page/create; create body `{"values":{...}}` |
| `GET /api/modules/{resource}/{id}` | Object-authorized details; confidential narrative restricted |
| `PATCH /api/modules/{resource}/{id}` | Admin allowed master-data fields only |
| `POST /api/modules/{resource}/{id}/transition` | Explicit legal state action with `{"status":"..."}` |

Dashboard analytics retain the organization's data label and evidence coverage. Confirmed progress is an unweighted mean of known activity progress; missing actuals remain unknown. The progress chart shows cumulative planned/confirmed completion dates from the current schedule, not a historical weighted-progress series or forecast. Matching separates accepted links, low confidence, unmatched, and pending review. No schema changes or new analytics dataset are required.

Resources: departments, units, locations, designations, skills, employees; clients,
contacts, opportunities, tenders, proposals, contracts; vendors, materials,
stores, material-requests, purchase-orders, receipts, movements; people,
inspections, quality-issues, safety, corrective-actions. Receipt creation credits
stock atomically; movement creation issues positive quantities to a project/team.
Orders require approved requests, receipts cannot exceed the order, and site
issues cannot create negative stock. Open corrective actions block issue/incident
closure. Employee project/team and all linked objects are checked on the server.
Existing authentication, Admin PM/TL assignment, review, schedule and import APIs
remain available. OpenAPI exposes the request contracts.

### Configuration and verification

Continue using root/backend/frontend `.env.example` templates and the central
settings/API client. Database/API URLs, CORS, session/cookies, input/upload/import
limits and provider/storage settings remain environment configuration. No backend
secret belongs in `VITE_*`. No production URL or shared worker password is added
to application source.

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_phase10
npm test
npm run build
npm run lint
.\.venv\Scripts\python.exe -m pip check
```

The backend verifier reads the configured `TEST_DATABASE_URL` without printing
it and uses disposable PostgreSQL schemas. See the verification report for actual
results, browser evidence, fixes, restart persistence and remaining operational
limitations. Vercel → Render → Neon remains the intended deployment path; live
provider deployment and Neon PITR are future operations, not claimed test results.
