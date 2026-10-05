"""Restart only API processes recorded by this Phase 10 verification run."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from backend.app.core.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--start', action='store_true', help='Start a separately configured verification API')
    args = parser.parse_args()
    settings = Settings()
    env = os.environ.copy()
    if args.browser:
        state_path = ROOT / '.audit/phase10-browser-state.json'
        state = json.loads(state_path.read_text())
        row = next(p for p in state['processes'] if p['kind'] == 'api')
        pid = row['pid']
        env.update(DATABASE_URL=settings.database_url, DB_SCHEMA=state['schema'], APP_ENV='test', API_PORT='8001', CORS_ORIGINS='http://127.0.0.1:5174', SESSION_COOKIE_SECURE='false', SESSION_COOKIE_SAMESITE='lax')
        prefix = 'phase10-browser-api'
    else:
        state_path = ROOT / '.audit/phase10-api-pid.txt'
        pid = int(state_path.read_text())
        prefix = 'phase10-api'
    # Validate process identity before stopping the recorded PID.
    if not args.start:
        probe = subprocess.run(['powershell','-NoProfile','-Command',f'(Get-CimInstance Win32_Process -Filter "ProcessId={pid}").CommandLine'], capture_output=True, text=True)
        if 'scripts/run_backend.py' not in probe.stdout.replace('\\','/'):
            raise RuntimeError('Recorded process is not the verification API; restart refused.')
        subprocess.run(['taskkill','/PID',str(pid),'/T','/F'], check=True, capture_output=True)
    with open(ROOT / '.audit' / (prefix+'.out.log'),'a') as out, open(ROOT / '.audit' / (prefix+'.err.log'),'a') as err:
        process = subprocess.Popen([sys.executable,'scripts/run_backend.py'],cwd=ROOT,env=env,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if args.browser:
        row['pid'] = process.pid
        state_path.write_text(json.dumps(state))
    else:
        state_path.write_text(str(process.pid))
    print('Recorded verification API restarted:', 'isolated browser' if args.browser else 'canonical local')


if __name__ == '__main__':
    main()
