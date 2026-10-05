"""Run genuine PostgreSQL regression checks without replacing Phase 9 evidence."""
import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values


def main():
    env = os.environ.copy()
    env['TEST_DATABASE_URL'] = dotenv_values('.env')['TEST_DATABASE_URL']
    args = [sys.executable, '-m', 'pytest', *(sys.argv[1:] or ['backend/tests']), '-q', '--tb=short', '-o', 'cache_dir=.audit/pytest-cache']
    result = subprocess.run(args, env=env, capture_output=True, text=True)
    Path('.audit/phase10-pytest.log').write_text(result.stdout+result.stderr, encoding='utf-8')
    print(result.stdout[-7000:])
    print('Backend exit code:', result.returncode)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
