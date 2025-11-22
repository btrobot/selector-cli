#!/usr/bin/env python3
"""
Selector CLI - Entry Point
Phase 1 MVP
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import src as a package
parent_path = Path(__file__).parent
sys.path.insert(0, str(parent_path))

from src.repl.main import main

if __name__ == '__main__':
    asyncio.run(main())
