# PRAVAHA — Phase 9 audit

## 1. Initial architecture

Inspected the current React/Vite frontend, FastAPI/Pydantic routes, services, SQLAlchemy repositories, PostgreSQL integration, Alembic revisions, Phase 7 matcher, Phase 8 execution intelligence, authentication/ownership, tests, environment examples and dashboards. Existing Git changes included the earlier frontend relocation; those changes were preserved. There is one runtime API and one PostgreSQL repository layer. Legacy Node/SQLite code remains only under migration/regression references. No Field Worker role was added.

Baseline: 311 backend tests, 42 Node tests, Phase 8 runtime/browser and migration evidence. Before edits, a source ZIP, custom-format PostgreSQL dump and fingerprints of every original table were saved privately under .audit. No database reset occurred.

## 2. Phase 9 changes

Added CSV/XLSX ingestion, immutable schedule snapshots, typed dependency persistence/traversal, structured TL fields, safe attachments, provider boundaries, scoped SQL search, shared PostgreSQL throttling, pool configuration, startup validation, request logs, Admin system visibility/project creation and deployment/recovery documentation. Added focused panels inside the existing dashboards. Preserved natural-language extraction, deterministic matching, PM authority, reconciliation and Phase 8 warning/memory behavior. No Phase 10 work.

Detailed file inventory: phase-9-files.json. Added backend services/repositories/routes/schema, one incremental migration, two test files, frontend import/search/health/evidence components and deployment configuration. Existing backend, client, dashboard and documentation files were extended.

## 3. Schedule ingestion

CSV/XLSX preview and commit are project-authorized. Headers map to supported fields; explicit empty mapping preserves unsupported columns. Required fields: activity ID/name/planned start/planned finish. ISO/native Excel dates, finite percentages/durations, duplicates, missing references, relationship/hierarchy cycles and cross-project teams are validated. XLSX formulas/macros/external links, large ZIP expansion and multiple worksheets are rejected. Iteration remains bounded even when worksheet dimensions are misleading.

Unsupported columns remain in extraColumns. Preview shows accepted/rejected rows, errors, warnings and changes. Commit reparses, binds checksum to file plus mapping and checks expectedVersionId under the organization lock. Any invalid row/graph blocks the entire import. Audit failure rolls back activities, versions, graph and audit together.

Limits: 5 MiB, 2,000 activities, 60 columns, 50 relationships per dependency cell and 10,000 graph edges. These are explicit capacity limits, not production-scale performance claims. Optional discipline/location normalize to empty values; missing progress remains unknown. Minimal imports support TL activity actions without a missing-key error.

## 4. Schedule versioning

First import preserves an immutable existing baseline snapshot. Project payload distinguishes baseline/current/previous version IDs. Versions record importer, time, format, filename, checksum, accepted/rejected counts, warnings and full normalized schedule rows. Comparison reports additions/removals and changed dates/durations/progress/dependencies/team/hierarchy/float. Comparison itself is audited.

Existing activity IDs, original reconciliation baselines, actuals, contributions and history survive imports. Removed activities are retired rather than deleted. Accepted retired evidence remains in institutional memory outside current execution coverage; pending links to retired rows get an honest schedule-version-change warning. Imported actuals have explicit provenance; PM-confirmed contributions take precedence. Historical snapshot progress can differ from preserved current execution progress by design.

## 5. Dependency graph

ScheduleDependency persists project/version/predecessor/successor/type/lag/time. FS/SS/FF/SF are supported; lag may be negative and is bounded/finite in the parser. Composite foreign keys enforce activity and version project isolation. Graph endpoints authorize project access and paginate in SQL. Matching remains based on the existing deterministic matcher, not inferred dependencies.

## 6. Downstream impact and risk

Traversal uses current persisted typed edges, calendar dates, start/finish variance, supplied lag and planned slack. Direct and transitive items include depth/path, source version, already-started state, target timing and explanation. Potential exposure is ESTIMATED, insufficient date evidence UNKNOWN, satisfied constraints NOT_APPLICABLE; graph availability is KNOWN. Traversal order is stable across reordered graph/activity inputs. No exact forecast dates, missing float or critical path are fabricated.

Negative float is a HIGH warning only when explicitly supplied. Existing overdue/missing-actual/stale/review/warning signals remain. Dependency warning transitions and intelligence snapshots use the existing transactional audit ledger. Portfolio graph loading is batched and retains the existing query-count regression limit.

## 7. OCR and attachment architecture

DocumentProcessor validates bytes and safe filenames; metadata includes project/update/uploader/time/MIME/size/checksum. Bytes are stored in PostgreSQL, deferred from ordinary metadata queries and included in backups. Downloads require ownership/project authorization and use attachment disposition/octet-stream/nosniff. TXT/CSV/XLSX/PDF/PNG/JPEG/WAV are supported within limits; files are never executed or rendered inline.

OCRProvider is a service boundary. No executable external OCR adapter is installed: defaults return NOT_CONFIGURED, configured names UNAVAILABLE, text null. Requests are audited. PDF checks are structural/magic/active-content heuristics, not complete PDF sanitization or malware scanning. Production malware policy and storage quotas remain operator work.

## 8. ASR architecture

ASRProvider is separate from routes/matching. Valid bounded WAV evidence can be uploaded; no microphone permission or fabricated transcription is requested. The TL UI explains that text is still required for matching. No external ASR adapter is implemented; explicit unavailable responses are tested and audited.

## 9. Advanced intelligence

AdvancedIntelligenceProvider isolates future candidate ranking. AI_PROVIDER/API_KEY/MODEL/BASE_URL are environment-only; keys are not returned or logged. There is no executable external provider adapter and no fabricated ranking. The deterministic Phase 7 matcher remains authoritative and PM review controls confirmed actual progress.

## 10. Search, memory and performance

Search uses SQL-filtered unions, counts, limit/offset and embedded organization/project/team scope across projects, current activities, field updates, versions, warnings, audit and grounded memory/audit details. Wildcards are escaped and statements are parameterized. Existing project memory retains historical evidence and feedback.

Added scope/entity/time and project audit indexes plus version/dependency/attachment indexes. Attachment bytes load lazily; graph portfolio queries are batched. Existing <=9-query portfolio regression passes without loosening the test. Import/search/version/dependency/attachment APIs have explicit bounds/pagination.

Remaining performance debt: organization-wide legacy snapshot writes/locks and unpaginated workspace collections; version metadata queries still deserialize stored JSON snapshots; substring search lacks a trigram/full-text index; intelligence input batches cap at 10,000 rows; impact results cap at 5,000. No production load benchmark was performed.

## 11. Security and observability

Argon2id passwords and hashed opaque expiring/revocable sessions are preserved. Authentication, generic errors, throttling, role/project/team/user-ID ownership and same-name ownership regressions pass. TL cannot import/review/see Admin intelligence; PM cannot inspect unrelated projects. Uploads require reporting TL ownership; Admin/PM downloads require project access.

Production configuration requires Secure cookies, SSL-required PostgreSQL, exact HTTPS CORS origins, disabled SQL echo and the shared PostgreSQL limiter. Authenticated production cookie mutations require an allowed Origin. Request bodies are bounded: 1 MiB ordinarily, 8 MiB for import/upload transport, 5 MiB decoded files. Trusted proxy addresses are configurable.

Shared login reservations are atomic PostgreSQL upserts in a separate transaction so failed-login rollback does not erase attempts. Two-instance/expiry tests pass; no Redis service was introduced. Request logs contain bounded request ID, route template, method, status, duration, role and error category. Uvicorn raw access logs are disabled. Checked credential values were absent from runtime logs; secrets remain in ignored .env/private files. See phase-9-secret-scan.json and phase-9-observability.json. Heuristic scans are not a guarantee against every possible secret format.

## 12. Database integrity and recovery

PostgreSQL is the persisted source of truth. Canonical migration and final consistency checks compared all original row counts and sorted full-row hashes: unchanged except the Alembic revision. Users/sessions/projects/activities/updates/reviews/contributions/warnings/audit remain intact. No disabled PM/TL operational assignments, unexpected roles, cross-project matches/contributions or unvalidated foreign keys were found. There are 39 validated foreign keys.

Private pre-change pg_dump was restored into a uniquely named separate database. Every restored row fingerprint matched; upgrade/schema check/readiness and Admin/PM/TL login/workspace passed. See phase-9-migration.json, phase-9-consistency.json and phase-9-restore.json. Production backup/PITR, encryption/retention and approved RPO/RTO remain NOT VERIFIED. Admin's operational backup status deliberately remains NOT_VERIFIED; a local drill is not proof of a deployed backup service.

## 13. Migrations and APIs

Added revision 0003_schedule_ingestion after 0002_execution_warnings. New version/dependency/attachment/login-bucket tables, indexes and composite ownership constraints are incremental. Downgrade/upgrade are tested in an isolated schema; canonical downgrade was not performed. Alembic check reports no new upgrade operations. Startup refuses an outdated schema.

README documents the new health/readiness/Admin/project/import/version/dependency/search/attachment/provider routes and structured TL fields. Existing auth/workspace/Admin/PM/TL/review/intelligence routes remain. Requests are Pydantic-validated and ownership is enforced server-side. API services share the existing transaction dependency and audit ledger.

## 14. Tests and exact commands

Node v24.21.0; npm 11.19.0; Python 3.12.14; PostgreSQL 18.6. Executed from D:/Coding/pravaha:

```powershell
node -v
npm -v
npm test
npm run lint
npm run build
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip install --dry-run --no-index --no-cache-dir -r backend/requirements.txt
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini check
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe .audit/phase9_setup.py
.\.venv\Scripts\python.exe .audit/phase9_runtime.py
.\.venv\Scripts\python.exe .audit/phase9_restore.py
.\.venv\Scripts\python.exe .audit/phase9_consistency.py
.\.venv\Scripts\python.exe .audit/phase9_verify.py
git diff --check
git check-ignore .env backend/.env .audit/phase9-runtime-env.json backend/.venv/pyvenv.cfg
```

The private verify wrapper reads TEST_DATABASE_URL without printing it and actually executes:
`python -m pytest backend/tests -q --tb=short -o cache_dir=.audit/pytest-cache`.
All database tests use unique disposable PostgreSQL schemas. The setup wrapper took the canonical migration proof, then started the API (`python scripts/run_backend.py`) and Vite (`node node_modules/vite/bin/vite.js`, frontend working directory) on isolated ports 52975/52974 and schema phase9_audit. Do not replay its CREATE SCHEMA step against the already-created schema. Private audit scripts are retained for inspection and read configuration from private environment files.

Node tests: 42 passed. Lint/build: exit 0. Backend: 337 passed, zero failures, one existing TestClient deprecation warning; final result is recorded in phase-9-tests.json. Pip dependency/manifest checks and Alembic check: pass. Existing project verification entry points are the test suites/build/lint/Alembic; seed/migration scripts are exercised through those integration tests rather than reseeding the live database.

Detected failures and corrections (no tests weakened):

| Exact failure | Classification | Correction / rerun |
| --- | --- | --- |
| SyntaxError: unmatched ')' | source code | Corrected repository query delimiter; focused/full tests rerun |
| INVALID_MAPPING: Column mappings must reference existing headers and supported target fields. | source code | Accept explicit empty target, preserve it instead of auto-alias fallback; checksum and UI-mapping integration tests rerun |
| AssertionError: assert 10 <= 9 | source code/performance | Archive classification folded into existing match query; original query-count bound retained; full suite rerun |
| UnicodeDecodeError: 'utf-16-le' codec can't decode byte 0x0a in position 1702: truncated data | source dependency-manifest encoding | Mixed UTF-16/UTF-8 file normalized to UTF-8, all 45 pins validated; identical pip dry-run command passed |
| Runtime audit AssertionError on expected >=4 Schedule-named events | audit harness | Two imports plus comparison create three Schedule-named events; dependency events have their own action; corrected expected event categories and reran |
| Runtime restart AssertionError: summary | audit environment | Restart activated changed archive-classification code; reran with the same final implementation loaded before/after restart and passed |
| range locator.fill deadline / CDP Runtime.evaluate timeout / transient locator misses | browser automation environment | Used range keyboard control, fresh snapshots and role locators; completed workflow and responsive checks |

Optional imported discipline/location initially could be absent while legacy TL actions index those keys. Normalization and a minimal-import-to-TL-action regression were added; the targeted test passed. Negative-float evidence uses the persisted schedule version ID, and graph traversal order was made stable across reordered inputs. No dependency resolver conflict remains. Existing Starlette TestClient/httpx deprecation emits one warning; it was not suppressed.

## 15. Runtime and browser verification

Real running API: health/readiness, all three logins, CSV and XLSX preview/import, baseline/current/previous snapshots, comparison, structured TL submission, deterministic recommendation, PM confirmation, 83% schedule actual, negative float and depth-2 dependency exposure, search/memory, TL feedback/Admin audit and attachment/provider fallback passed. A real backend process restart preserved sessions, versions, graph, attachment bytes, actuals and intelligence; warning IDs, status and evidence were compared across the restart too. Logout revocation passed. See phase-9-runtime.json.

Real in-app browser: Home-to-PM/TL/Admin login; PM uploaded/previewed/imported CSV, compared versions and searched records; TL submitted 9 spools/Crane 2 at 85% with a real CSV attachment, loaded persisted metadata and observed NOT_CONFIGURED OCR; PM inspected attachment and match evidence and confirmed with feedback; TL later saw the exact reviewed feedback. Admin health/project creation/search/activity were checked. The activity timeline filter returned two grounded records for the browser observation/confirmation, and its audit detail showed the exact PM feedback and 85% progress. Console warning/error logs were empty during checked workflow.

Home, PM import/intelligence/search, TL structured composer and Admin system/project/search were checked at 1440/1024/768/518: 16 measured cases, no document overflow, no measured controls outside viewport bounds, no broken images. Scrollable tables retain their containers. Measurements: phase-9-responsive.json. Visually inspected screenshot: phase-9-intelligence.jpg. One initial PM login attempt showed a generic credentials error; the same verified audit credentials subsequently signed in. No unverified root-cause claim is made for that transient attempt.

## 16. Deployment readiness

Prepared environment-driven managed PostgreSQL SSL/pool configuration, explicit migration release step, startup validation, PORT-aware launcher, trusted proxy configuration, Vercel SPA configuration, backend Dockerfile and private-data exclusions. Deployment and recovery runbook: phase-9-deployment.md. No cloud deployment, container build or real production HTTPS/CORS/cookie path was tested. No automatic deployment occurred.

Provider references checked: [Vercel rewrites](https://vercel.com/docs/routing/rewrites), [Render FastAPI hosting](https://render.com/docs/deploy-fastapi), [SQLAlchemy pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html), [openpyxl security](https://openpyxl.readthedocs.io/en/stable/). Neon documentation fetch was unavailable; no live Neon configuration claim is made.

## 17. Known limitations

Direct P6/MS Project formats are NOT IMPLEMENTED; normalized CSV/XLSX exports are supported. External OCR/ASR/AI adapters are NOT IMPLEMENTED; graceful fallback boundaries are implemented/tested. There is no critical-path solver or exact future-date prediction. Work calendars/resource constraints are not modeled; variance/exposure uses calendar days. Uploads have no antivirus service, organization quota or object-store adapter. Logical restores were tested locally; cloud PITR was not.

## 18. Remaining technical debt

Legacy organization snapshots/locks, unpaginated workspace collections, full JSON version metadata reads, substring-search indexing, bounded intelligence aggregation, retention/quotas, clock-driven warning refresh and the existing TestClient warning remain. Shared throttling removes process-local-only deployment state, but production multiworker/abuse-load testing is still required. Production telemetry/alerts/backup operations need deployment-specific configuration. Docker image build and clean-host installation were not verified; existing environment manifest/dependency validation passed.

## 19. Not verified, blockers and final status

Local implementation/regression/runtime/restore/browser verification passed (see artifacts). Production deployment, actual Neon TLS/pool integration, production HTTPS cookie/CORS/proxy behavior, multiworker load and production backup/PITR are NOT VERIFIED. No production destination/domain/credentials were provided and deployment was explicitly not authorized by this request.

The prompt prohibits claiming production readiness without an actually tested production deployment. Therefore the required production-readiness declaration is not supported, despite passing local checks. The remaining blocker to that declaration is an explicitly authorized deployment/staging verification with real production configuration and operations evidence. Phase 10 was not started.



Cleanup: temporary browser tabs closed and viewport reset. Only audit-created API/frontend processes were stopped. The PostgreSQL cluster, canonical database, isolated verification database/schema, pre-change backups and audit evidence were preserved for inspection.

PHASE 9 NOT COMPLETE
