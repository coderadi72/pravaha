"""Isolated browser fixture copied only from synthetic Phase 10 demo records."""
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from datetime import UTC, datetime
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from backend.app.core.config import Settings
from backend.app.core.security import hash_password
from backend.app.db.session import create_engine_and_factory
from backend.app.db.base import Base
from backend.app import models as m

ROOT = Path(__file__).resolve().parents[1]


def main(phase=10, organization_id='DEMO-phase10', project_id=None):
    if phase not in {10, 12}:
        raise ValueError("Only the existing Phase 10 / Phase 12 verification harness is supported.")
    api_port, vite_port = (8001, 5174) if phase == 10 else (8003, 5176)
    settings = Settings()
    schema = f'p{phase}_browser_'+uuid4().hex
    env = os.environ.copy()
    # These known fixtures exist only in an isolated test schema, never the canonical DB.
    fixtures = [('BROWSER-ADMIN','ADMIN','BrowserAdminPass123!'),('BROWSER-PM','PROJECT_MANAGER','BrowserManagerPass123!'),('BROWSER-TL','TEAM_LEADER','BrowserLeaderPass123!'),('BROWSER-WF','WORKFORCE','BrowserWorkerPass123!'),('BROWSER-HR','DEPARTMENT','BrowserPeoplePass123!')]
    admin_engine = create_engine(settings.database_url)
    source_engine, source_factory = create_engine_and_factory(settings)
    with source_factory() as session:
        org = session.get(m.Organization, organization_id)
        if not org or not any(word in org.data_label.lower() for word in ('demo', 'synthetic', 'demonstration')):
            raise ValueError('Only an existing labelled synthetic organization may be copied.')
        if project_id is None:
            project_id = session.scalar(select(m.ProjectManagerAssignment.project_id).join(m.Project).where(m.Project.organization_id == organization_id).order_by(m.Project.id))
        project = session.get(m.Project, project_id)
        if not project or project.organization_id != organization_id or not session.get(m.ProjectManagerAssignment, project_id):
            raise ValueError('Existing assigned synthetic project required.')
        team_id = session.scalar(select(m.TeamLeaderAssignment.team_id).join(m.Team).where(m.Team.project_id == project_id).order_by(m.Team.id))
    source_engine.dispose()
    with admin_engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    test_settings = Settings(_env_file=None,database_url=settings.database_url,db_schema=schema,app_env='test',api_port=api_port,cors_origins=[f'http://127.0.0.1:{vite_port}'])
    engine, factory = create_engine_and_factory(test_settings)
    config = Config(str(ROOT / 'backend/alembic.ini'))
    with engine.begin() as connection:
        config.attributes['connection'] = connection
        command.upgrade(config,'head')
        source = settings.db_schema
        for table in Base.metadata.sorted_tables:
            name, columns = table.name, table.c
            if name in {'legacy_schema_migrations','login_rate_buckets'}: continue
            if phase == 12 and name == 'sessions': continue
            if name == 'organizations': condition = 'id = :org'
            elif 'organization_id' in columns: condition = 'organization_id = :org'
            elif 'project_id' in columns: condition = f'project_id IN (SELECT id FROM "{source}".projects WHERE organization_id = :org)'
            elif 'field_update_id' in columns: condition = f'field_update_id IN (SELECT u.id FROM "{source}".field_updates u JOIN "{source}".projects p ON p.id=u.project_id WHERE p.organization_id = :org)'
            elif 'employee_id' in columns: condition = f'employee_id IN (SELECT id FROM "{source}".employees WHERE organization_id = :org)'
            elif 'user_id' in columns: condition = f'user_id IN (SELECT id FROM "{source}".users WHERE organization_id = :org)'
            else: raise ValueError('Unscoped fixture copy refused: '+name)
            column_list = ','.join('"'+c.name+'"' for c in table.columns)
            connection.execute(text(f'INSERT INTO "{schema}"."{name}" ({column_list}) SELECT {column_list} FROM "{source}"."{name}" WHERE {condition}'),{'org':organization_id})
    with factory.begin() as session:
        for identifier, role, password in fixtures:
            session.add(m.User(id=identifier,organization_id=organization_id,email=identifier.lower()+'@test.invalid',login_id=identifier.lower(),full_name=identifier.replace('-',' '),role=role,password_hash=hash_password(password),active=True,created_at=datetime.now(UTC)))
        session.flush()
        session.get(m.ProjectManagerAssignment,project_id).user_id='BROWSER-PM'
        if team_id:
            session.get(m.TeamLeaderAssignment,team_id).user_id='BROWSER-TL'
        session.add(m.DepartmentGrant(user_id='BROWSER-HR',capability='people',granted_by='BROWSER-ADMIN'))
        session.add(m.DepartmentGrant(user_id='BROWSER-HR',capability='hr-confidential',granted_by='BROWSER-ADMIN'))
    engine.dispose(); admin_engine.dispose()
    env.update(DATABASE_URL=settings.database_url, DB_SCHEMA=schema, APP_ENV='test', API_PORT=str(api_port), CORS_ORIGINS=f'http://127.0.0.1:{vite_port}', SESSION_COOKIE_SECURE='false', SESSION_COOKIE_SAMESITE='lax', VITE_API_BASE_URL=f'http://127.0.0.1:{api_port}/api', VITE_HOST='127.0.0.1', VITE_PORT=str(vite_port))
    creation = getattr(subprocess,'CREATE_NO_WINDOW',0)
    logs = []
    for kind, args in [('api',[sys.executable,'scripts/run_backend.py']),('vite',['cmd','/c','npm run dev'])]:
        out = open(ROOT / '.audit' / (f'phase{phase}-browser-'+kind+'.out.log'),'w')
        err = open(ROOT / '.audit' / (f'phase{phase}-browser-'+kind+'.err.log'),'w')
        process = subprocess.Popen(args,cwd=ROOT,env=env,stdout=out,stderr=err,creationflags=creation)
        logs.append({'kind':kind,'pid':process.pid})
    (ROOT / f'.audit/phase{phase}-browser-state.json').write_text(json.dumps({'schema':schema,'processes':logs,'organization':organization_id,'project':project_id}),encoding='utf-8')
    print(f'Isolated synthetic browser fixture started on frontend {vite_port} / API {api_port}. Canonical data was not changed.')


if __name__ == '__main__':
    main()
