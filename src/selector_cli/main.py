"""
Selector CLI - Main entry point
"""
import asyncio
import sys
import argparse
import logging
from .repl.main import SelectorREPL


def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Selector CLI - Interactive web element selection and code generation tool')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode with detailed logging')
    args = parser.parse_args()

    # Setup logging
    setup_logging(debug=args.debug)

    try:
        # Run REPL
        asyncio.run(SelectorREPL(debug=args.debug).run())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
