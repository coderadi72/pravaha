"""Run from the project root: python -m scripts.seed."""
from backend.app.core.config import Settings
from backend.app.db.seed import seed_database
from backend.app.db.session import create_engine_and_factory


def main():
    settings = Settings()
    engine, factory = create_engine_and_factory(settings)
    credentials = {f"SEED_{role}_{field}": getattr(settings, f"seed_{role.lower()}_{field.lower()}") for role in ("ADMIN", "PM", "TL") for field in ("EMAIL", "PASSWORD")}
    try:
        with factory.begin() as session:
            result = seed_database(session, credentials)
        print("Demo data seeded; credentials came from environment." if result["seeded"] else "Existing organization found; seeding skipped without changing data.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
