# PostgreSQL persistence

PostgreSQL is PRAVAHA's canonical database. The API uses SQLAlchemy 2.x and never
opens SQLite. Configure `DATABASE_URL` in the root or backend `.env`; changing it
to a compatible Neon PostgreSQL URL requires no application source change.

## Schema and migrations

From the project root, with backend dependencies installed:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
python -m alembic -c backend/alembic.ini current
```

The initial revision creates organization/user/project/team relationships,
assignments, schedule activities and baselines, field updates, intelligence,
reviews/history, contributions, audit events, hashed sessions, and legacy
SQLite migration provenance. Alembic owns current schema history. Startup never
drops or recreates tables. IDs remain stable text values during import; new
workflow IDs use a consistent entity prefix plus UUID.

`team_leader_assignments` is the single authoritative leader relation, with one
team per leader and one leader per team. Team JSON is presentation data and is
overridden by this relation when loaded. Project-manager assignments permit one
manager per project. Foreign keys, role checks, unique/case-insensitive emails,
and indexes enforce identity and lookup integrity. JSONB retains existing
workflow/evidence/baseline contracts without duplicating model calculations.

Every snapshot mutation takes an organization row lock before reading workflow
state. Persistence writes only changed relationships/rows; review history is
append-only. Workflow, human audit, and matcher audit share one transaction.

## Demo seeding

Configure distinct `SEED_ADMIN_EMAIL`, `SEED_PM_EMAIL`, `SEED_TL_EMAIL` and their
`SEED_*_PASSWORD` values. All three passwords must meet the documented policy.
Blank or invalid configuration fails before writes; no default passwords exist.

```powershell
python -m scripts.seed
```

`seed/demo.json` is labeled demo data captured from the completed Phase 7
dataset. Only credential-enabled PM-001 and TL-001 receive operational demo
assignments. Other demo identities remain disabled and unassigned. Seeding is
transactional and skips existing organizations without changing their data.

## Preserve legacy SQLite data

Legacy database files are migration/reference artifacts, never runtime inputs.
Back up PostgreSQL separately before administrative migration operations.
Run Alembic first, then choose an **empty target database or isolated schema**.
Do not seed before importing existing data.

```powershell
python -m scripts.migrate_sqlite --source database/legacy/pravaha.sqlite --report database/legacy/import-report.json
```

The importer uses SQLite's online backup API before reading data, including
committed WAL pages. It opens the source read-only, validates integrity and
foreign keys, rejects a populated PostgreSQL target, and imports atomically.
It compares row counts and every persisted value for all source tables. The
report gives SQLite/PostgreSQL/difference counts. Legacy migration history moves
to `legacy_schema_migrations`; leader rows derive from `teams.team_leader_id`.
Users, organizations, projects, teams, schedules, field updates, matches,
reviews/history, audit events, contributions, assignments and sessions retain
IDs and content. Invalid/ambiguous legacy assignments stop the import instead
of silently discarding records.

Password hashes are preserved. Authentication supports the old Node Argon2id
encoding and standard PHC Argon2id; successfully authenticated legacy hashes can
be upgraded without resetting passwords. Session SHA-256 hashes, user IDs and
expiry also migrate safely; expired sessions stay expired. No plaintext token
or password is needed or written in the report.

## Dedicated database tests

Set `TEST_DATABASE_URL` to a PostgreSQL database the test user may create schemas
in. Pytest creates a unique schema per test, executes Alembic, and removes only
that exact test schema. Tests never reset an application database. SQLite is
used solely to construct/import legacy fixtures, never as a replacement test
or production database.


Phase 8 migration `0002_execution_warnings` adds one indexed warning lifecycle table
with project/activity foreign keys and constrained status. Existing workflow rows,
IDs, baselines and contributions are preserved. Warning history and intelligence
changes reuse `audit_events`; no duplicate timeline store is created.
