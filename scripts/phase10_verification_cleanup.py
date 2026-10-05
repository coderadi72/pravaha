"""Remove only this run's disposable schema and recorded verification processes."""
import json
from pathlib import Path
import re
import subprocess
from sqlalchemy import create_engine, text
from backend.app.core.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def stop(pid, expected):
    result = subprocess.run(['powershell','-NoProfile','-Command',f'(Get-CimInstance Win32_Process -Filter "ProcessId={int(pid)}").CommandLine'],capture_output=True,text=True)
    command = result.stdout.replace('\\','/')
    if not command.strip():
        return
    if expected not in command:
        raise RuntimeError('Unrecognized recorded process; cleanup refused.')
    subprocess.run(['taskkill','/PID',str(int(pid)),'/T','/F'],check=True,capture_output=True)


def main():
    path = ROOT / '.audit/phase10-browser-state.json'
    state = json.loads(path.read_text())
    schema = state['schema']
    settings = Settings()
    if not re.fullmatch(r'p10_browser_[0-9a-f]{32}',schema) or schema == settings.db_schema:
        raise RuntimeError('Disposable schema validation failed.')
    if not state.get('cleanedUp'):
        for row in state['processes']:
            stop(row['pid'], 'scripts/run_backend.py' if row['kind'] == 'api' else 'npm run dev')
    stop(int((ROOT / '.audit/phase10-api-pid.txt').read_text()),'scripts/run_backend.py')
    engine = create_engine(settings.database_url)
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    engine.dispose()
    state['cleanedUp'] = True
    path.write_text(json.dumps(state))
    print('Recorded verification processes stopped; disposable browser schema removed. Canonical data retained.')


if __name__ == '__main__':
    main()
