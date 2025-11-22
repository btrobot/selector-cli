"""
Integration test - Tests full CLI workflow with local test page
"""
import sys
from pathlib import Path

# Add parent directory to path
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

import asyncio
from src.repl.main import SelectorREPL

async def test_integration():
    """Test full workflow with automated commands"""

    # Get local test page path
    test_page = Path(__file__).parent.parent.parent / 'selector-explorer' / 'test_page.html'

    if not test_page.exists():
        print(f"[SKIP] Local test page not found at: {test_page}")
        print("This test requires the selector-explorer test page")
        return

    test_url = f'file:///{test_page.absolute().as_posix()}'

    print("="*60)
    print("Integration Test - Selector CLI")
    print("="*60)
    print(f"\nUsing test page: {test_url}\n")

    # Create REPL instance
    repl = SelectorREPL()

    # Initialize browser manually
    from src.core.browser import BrowserManager
    repl.context.browser = BrowserManager()
    await repl.context.browser.initialize(headless=True)

    # Test commands
    commands = [
        ('open', test_url, "Open test page"),
        ('scan', None, "Scan for elements"),
        ('list', None, "List all scanned elements"),
        ('add input', None, "Add all input elements"),
        ('count', None, "Count collection"),
        ('show', None, "Show collection details"),
        ('clear', None, "Clear collection"),
        ('add button where type="submit"', None, "Add submit button"),
        ('count', None, "Count after filter"),
    ]

    print("Testing commands:")
    print("-" * 60)

    for cmd_str, arg, description in commands:
        if arg:
            full_cmd = f"{cmd_str} {arg}"
        else:
            full_cmd = cmd_str

        print(f"\n[{description}]")
        print(f"  Command: {full_cmd}")

        try:
            command = repl.parser.parse(full_cmd)
            result = await repl.executor.execute(command, repl.context)

            # Show first 200 chars of result
            result_preview = result[:200] + "..." if len(result) > 200 else result
            print(f"  Result: {result_preview}")

        except Exception as e:
            print(f"  Error: {e}")
            await repl.context.browser.close()
            return

    # Cleanup
    await repl.context.browser.close()

    print("\n" + "="*60)
    print("[OK] Integration test complete!")
    print("="*60)

if __name__ == '__main__':
    asyncio.run(test_integration())
