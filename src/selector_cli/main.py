"""
Selector CLI - Main entry point
"""
import asyncio
import sys
from src.cli.repl import REPL


def main():
    """Main entry point"""
    try:
        # Run REPL
        asyncio.run(REPL().run())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
