"""Fill missing initial legacy schedule keys in the newly created Phase 10 demo."""
from sqlalchemy import select
from backend.app.models import Project, ScheduleActivity
from backend.app.core.config import Settings
from backend.app.db.session import create_engine_and_factory


def main():
    engine, factory = create_engine_and_factory(Settings())
    count = 0
    with factory.begin() as session:
        for project in session.scalars(select(Project).where(Project.organization_id == 'DEMO-phase10')):
            payload = project.payload_json
            disciplines = sorted({row.payload_json['discipline'] for row in session.scalars(select(ScheduleActivity).where(ScheduleActivity.project_id == project.id))})
            project.payload_json = {**payload, 'location':payload.get('location') or payload['site'], 'disciplines':payload.get('disciplines') or disciplines}
        for row in session.scalars(select(ScheduleActivity).join(Project).where(Project.organization_id == 'DEMO-phase10')):
            if 'level' not in row.payload_json:
                row.payload_json = {**row.payload_json, 'level':'L6', 'progress':row.payload_json.get('actualProgress',0)}
                row.baseline_json = {**row.baseline_json, 'level':'L6', 'progress':row.baseline_json.get('actualProgress',0)}
                count += 1
    engine.dispose()
    print('Missing initial demo schedule keys corrected:', count)


if __name__ == '__main__':
    main()
