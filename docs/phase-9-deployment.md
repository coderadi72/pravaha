# Phase 9 deployment and recovery runbook

Selected target architecture: Vercel frontend -> Render native Python FastAPI service -> Neon PostgreSQL. Configuration is prepared; no cloud deployment has been performed or verified. Docker is optional and is not required for the selected Render native build/start path.

## Frontend on Vercel

Set root directory `frontend`, install `npm install` from the repository workspace, build `npm run build`, output `dist`.
Set `VITE_API_BASE_URL=https://<api-host>/api` at build time. Frontend variables contain no database or provider credentials.
`frontend/vercel.json` supplies SPA routing. Use a same-site custom frontend/API domain when possible.
Different-site deployments require `SESSION_COOKIE_SAMESITE=none` and Secure cookies; browser third-party-cookie restrictions may still prevent login. Test this with the actual production domains.

## FastAPI hosting on Render

Python 3.12+, install `pip install -r backend/requirements.txt`.
Build container from repository root: `docker build -f backend/Dockerfile -t pravaha-api .`.
The selected Render configuration uses the native Python build and starts `python scripts/run_backend.py`; the Docker command is an optional alternative, not a Phase 9 target gate.
Set `API_HOST=0.0.0.0`; hosting `PORT` overrides `API_PORT`.
Run `alembic -c backend/alembic.ini upgrade head` once in the release step, then `alembic -c backend/alembic.ini check`.
Startup refuses an outdated schema. Migrations are not run automatically by web workers.
Readiness `/api/ready`; public minimal health `/api/health`; Admin-only `/api/admin/system`.

## Managed PostgreSQL / Neon

Set `DATABASE_URL=postgresql://<user>:<password>@<provider-host>/<database>?sslmode=require` from a secret manager.
Use a provider's direct connection for migrations and pg_dump/pg_restore. Use their pooled URL for web workers when recommended by the provider.
Production settings: `APP_ENV=production`, `RATE_LIMIT_BACKEND=postgresql`, `SESSION_COOKIE_SECURE=true`, `ENABLE_API_DOCS=false`, `SQL_ECHO=false`, `CORS_ORIGINS=https://<exact-frontend-host>`.
No wildcard origins. Authenticated cookie mutations require an allowed Origin in production.
Set `TRUSTED_PROXY_IPS` to the actual reverse-proxy addresses; do not blindly trust all client forwarding headers.
Pool controls: `DB_POOL_MODE=queue` (default) or `null`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, `DB_CONNECT_TIMEOUT`.
Prepared statements are disabled for pooled compatibility. Budget total connections across all workers.
DB_SCHEMA defaults to public; alternate schemas use a strict search path without public fallback.
All provider defaults are `none`. Setting a provider name without an installed adapter returns UNAVAILABLE; no text is fabricated.

## Logs and uploads

Structured request logs contain a bounded request ID, route template, method, status, duration, role and error category. They omit request bodies, queries, passwords, cookie tokens, API keys and URLs with credentials.
Uvicorn access logging is disabled. Configure host log retention, access control and alerting.
Attachments (including bytes) are persisted in PostgreSQL with authenticated downloads; database backups therefore include them. Each upload is limited to 5 MiB. No public directory or inline rendering is used.
Validation is not malware scanning. Production rollout needs operational storage quotas, antivirus scanning policy and retention decisions.

## Backup and restore

Keep encrypted backups outside the application host and restrict access. Never commit dumps, credentials or .env files.
Configure PGPASSFILE securely; avoid putting database credentials directly in shell history or process arguments.
Daily custom-format logical backup (use a direct connection):

```powershell
pg_dump --format=custom --file=pravaha-YYYYMMDD.pgdump --host=<host> --username=<backup-user> --dbname=<database>
pg_restore --list pravaha-YYYYMMDD.pgdump
```

Restore into a separately named verification database provisioned by an operator; never overwrite the live database to test recovery:

```powershell
pg_restore --exit-on-error --no-owner --dbname=pravaha_restore_check pravaha-YYYYMMDD.pgdump
alembic -c backend/alembic.ini check
```

Set DATABASE_URL to the verification database before that schema check. Compare row counts and representative users/projects/reviews/warnings/versions/attachment checksums; start a verification API and check login, workspace, review history and attachment download. Record restore duration and recovery point.
A consistent logical dump includes all committed rows at its snapshot, including audit and attachments. Use provider PITR/continuous backup for lower recovery-point targets; verify actual plan retention and restore procedure with the provider.
Logical dumps do not archive PostgreSQL WAL for PITR. Do not copy a live PostgreSQL data directory as a backup.
Suggested initial policy: daily backup, weekly isolated restore drill, 30-day encrypted retention; approve actual RPO/RTO and policy before production.

## Operator checklist

Run the documented test/build/lint/schema checks, test actual HTTPS cookie/CORS behavior, migration privileges, provider pool configuration, multiworker throttling, health probes, log redaction, encrypted backup/restore and production workload limits. No production performance or cloud readiness claim follows solely from local tests.


## References

Official configuration references consulted: [Vercel rewrite configuration](https://vercel.com/docs/routing/rewrites), [Render FastAPI startup](https://render.com/docs/deploy-fastapi), and [SQLAlchemy connection pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html). Deployment examples require verification on the actual selected host. Neon documentation could not be fetched during this audit; no live Neon connection was tested.
