#!/usr/bin/env python3
"""
Selector CLI - Entry Point
Phase 1 MVP
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from repl.main import main

if __name__ == '__main__':
    asyncio.run(main())
