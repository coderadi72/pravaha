# Local audit PostgreSQL setup

This machine was verified with a portable PostgreSQL 18.6 cluster under
`.tools/postgresql/data`, bound to 127.0.0.1:55432. This local cluster remains
running after the audit. Root `.env` privately selects `pravaha_phase71`, the
canonical preserved copy; `TEST_DATABASE_URL` selects `pravaha_test`.
`pravaha_runtime` contains disposable browser/API verification records.
The initially affected import copy `pravaha` is retained only for diagnostics.
The original SQLite files and coherent backups remain under database/legacy and
.migration-backups. Never reset/drop these databases as part of normal startup.

The PostgreSQL distribution/data and private owner/application credentials
are ignored local artifacts, not source-controlled deployment infrastructure.
If the cluster is stopped, a local administrator can restart this same data
folder using the portable vendor binaries (do not rerun initdb):

```powershell
Start-Process -FilePath .tools/postgresql/18.6/pgsql/bin/pg_ctl.exe -ArgumentList 'start','-D','D:/Coding/pravaha/.tools/postgresql/data','-l','D:/Coding/pravaha/.audit/postgres.log','-o','"-h 127.0.0.1 -p 55432"' -WindowStyle Hidden -Wait
```

This machine's restricted sandbox could not use pg_ctl's restricted-token
launcher; approved local process startup succeeded. No authentication protection
was disabled. Alternatively configure DATABASE_URL/TEST_DATABASE_URL for your
own PostgreSQL service/provider, apply Alembic, and import existing data into an
empty target before use. Use the regular root README commands to start FastAPI
and Vite; temporary audit application servers were stopped after verification.
