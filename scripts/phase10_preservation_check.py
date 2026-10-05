"""Compare pre-migration rows, ignoring only the added nullable user column."""
import json
from pathlib import Path
from sqlalchemy import text
from backend.app.core.config import Settings
from backend.app.db.session import create_engine_and_factory


def main():
    before = json.loads(Path('.audit/phase10-before.json').read_text())
    engine, _ = create_engine_and_factory(Settings())
    with engine.connect() as connection:
        after = {}
        for table in before:
            expression = "(to_jsonb(t)-'login_id')::text" if table == 'users' else 'to_jsonb(t)::text'
            sql = f'SELECT count(*) AS count, md5(coalesce(string_agg({expression},\'\' ORDER BY {expression}),\'\')) AS digest FROM "{table}" t'
            after[table] = dict(connection.execute(text(sql)).mappings().one())
    engine.dispose()
    changed = [table for table in before if before[table] != after[table]]
    result = {'tables': len(before), 'preserved': len(before)-len(changed), 'changed': changed}
    Path('.audit/phase10-preservation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
    if changed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
