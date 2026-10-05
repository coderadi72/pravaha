"""Start the canonical API using configuration, without a Node API process."""
from pathlib import Path
import argparse
import sys
import os
import logging

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.core.config import Settings
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run the PRAVAHA FastAPI backend")
    parser.add_argument("--reload", action="store_true", help="Reload Python application files during development")
    options = parser.parse_args()
    settings = Settings()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    uvicorn.run("backend.app.main:app", host=settings.api_host, port=int(os.environ.get("PORT", settings.api_port)),
                access_log=False, proxy_headers=True, forwarded_allow_ips=settings.trusted_proxy_ips,
                reload=options.reload, reload_dirs=["backend"] if options.reload else None)


if __name__ == "__main__":
    main()
