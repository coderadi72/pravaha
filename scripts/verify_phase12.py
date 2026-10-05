"""Current PostgreSQL evidence; keeps earlier phase verification logs intact."""
import os
from pathlib import Path
import subprocess
import sys
from dotenv import dotenv_values

env = os.environ.copy()
env["TEST_DATABASE_URL"] = dotenv_values(".env")["TEST_DATABASE_URL"]
env["PYTHONPATH"] = str(Path.cwd())
result = subprocess.run([sys.executable, "-m", "pytest", *(sys.argv[1:] or ["backend/tests"]), "-q", "--tb=short", "-o", "cache_dir=.audit/pytest-cache"], env=env, capture_output=True, text=True)
Path(".audit").mkdir(exist_ok=True)
Path(".audit/phase12-pytest.log").write_text(result.stdout + result.stderr, encoding="utf-8")
print(result.stdout[-9000:])
print("Backend exit code:", result.returncode)
raise SystemExit(result.returncode)
