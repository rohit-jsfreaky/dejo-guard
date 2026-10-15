"""Dejo Guard: ArmorIQ decides every browser-agent action by what it means on the page."""

from __future__ import annotations

import sys

from .cli import main

__all__ = ["main"]

if __name__ == "__main__":
    sys.exit(main())
