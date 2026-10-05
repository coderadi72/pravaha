"""Authorized, repeat-safe synthetic provisioning with a private credential export."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from backend.app.core.config import Settings
from backend.app.db.session import create_engine_and_factory
from backend.app.db.demo_organization import generate
from backend.app.models import User

ROOT = Path(__file__).resolve().parents[1]


def private_directory():
    path = ROOT / '.audit' / 'provisioning'
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == 'nt':
        owner = subprocess.run(['whoami'], check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r', owner+':(OI)(CI)F'], check=True, capture_output=True)
    else:
        path.chmod(0o700)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--admin-id', required=True, help='Existing enabled Admin authorizing demo provisioning')
    parser.add_argument('--namespace', default='phase10')
    parser.add_argument('--pms', type=int, default=20)
    parser.add_argument('--teams-per-pm', type=int, default=8)
    parser.add_argument('--workers-per-team', type=int, default=20)
    args = parser.parse_args()
    engine, factory = create_engine_and_factory(Settings())
    export_path = private_directory() / (args.namespace+'-credentials.json')
    if export_path.parent.resolve() != (ROOT / '.audit/provisioning').resolve():
        raise ValueError('Invalid namespace.')
    created_export = False
    try:
        with factory.begin() as session:
            admin = session.get(User, args.admin_id)
            if not admin or admin.role != 'ADMIN' or not admin.active or not admin.password_hash:
                raise ValueError('An existing enabled Admin is required.')
            report, credentials = generate(session, args.namespace, args.pms, args.teams_per_pm, args.workers_per_team)
            if credentials:
                # Exclusive creation preserves first credentials on rerun. Folder ACL is applied before writing.
                descriptor = os.open(export_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                created_export = True
                with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                    json.dump({'label':'PRIVATE DEMO INITIAL CREDENTIALS — synthetic only; do not publish or commit', 'authorizedBy':args.admin_id, 'organizationId':report['organizationId'], 'accounts':credentials}, stream, indent=2)
            elif not export_path.exists():
                raise ValueError('Dataset exists but initial export is unavailable. Passwords cannot be recovered; do not reseed.')
        print(json.dumps(report))
        print('Initial credentials are in the restricted .audit/provisioning directory. Passwords are never printed.')
    except Exception:
        if created_export:
            export_path.unlink()
        raise
    finally:
        engine.dispose()


if __name__ == '__main__':
    main()
