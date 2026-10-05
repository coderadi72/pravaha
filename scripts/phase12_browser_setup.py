"""Reuse the safe synthetic-only browser fixture with separate Phase 12 processes."""
from phase10_browser_setup import main

if __name__ == "__main__":
    main(phase=12)
