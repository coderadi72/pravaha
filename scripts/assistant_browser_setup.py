"""Reuse the isolated harness for the requested existing synthetic project only."""
from scripts.phase10_browser_setup import main

if __name__ == "__main__":
    main(12, organization_id="ORG-OIL-DEMO", project_id="PRJ-001")
