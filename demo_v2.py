"""
V2 Demo Script - Showcase three-layer architecture features
Run with: python demo_v2.py
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from selector_cli.core.browser import BrowserManager
from selector_cli_v2.v2.context import ContextV2
from selector_cli_v2.v2.parser import ParserV2
from selector_cli_v2.v2.executor import ExecutorV2


async def demo():
    """Run V2 demo"""
    print("=" * 70)
    print("Selector CLI v2.0 - Three-Layer Architecture Demo")
    print("=" * 70)

    # Setup
    ctx = ContextV2(enable_history_file=False)
    parser = ParserV2()
    executor = ExecutorV2(ctx)
    browser = BrowserManager()
    await browser.initialize(headless=False)
    ctx.browser = browser

    try:
        # Load demo page
        test_file = Path(__file__).parent / "tests" / "test_role_button.html"
        if not test_file.exists():
            print(f"Demo file not found: {test_file}")
            return

        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url
        print(f"\nLoaded demo page: {test_url}")
        print("\nDemo page contains:")
        print("  - Traditional <button> elements")
        print("  - <div role=\"button\"> custom elements")
        print("  - <input> fields")
        print("  - <a> links")
        input("\nPress Enter to continue...")

        # Demo 1: Traditional workflow
        print("\n" + "=" * 70)
        print("Demo 1: Traditional workflow")
        print("=" * 70)
        print("Commands:")
        print("  1. scan                    # Scan page for elements")
        print("  2. add button              # Add buttons to workspace")
        print("  3. list                    # Show workspace")

        input("\nPress Enter to execute...")

        print("\n[1/3] Executing: scan")
        cmd = parser.parse("scan")
        success, result = await executor.execute(cmd)
        print(f"✓ Found {len(ctx.candidates)} elements in candidates")

        print("\n[2/3] Executing: add button")
        cmd = parser.parse("add button")
        success, result = await executor.execute(cmd)
        print(f"✓ Added {result} buttons to workspace")

        print("\n[3/3] Executing: list")
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        print(f"\n{result}")

        input("\nPress Enter to continue to Demo 2...")

        # Demo 2: Find role=button elements
        print("\n" + "=" * 70)
        print("Demo 2: Finding custom role='button' elements")
        print("=" * 70)
        print("Commands:")
        print("  1. find div where role=\"button\"  # Query DOM for custom buttons")
        print("  2. list temp                       # Review results in temp")
        print("  3. add from temp                   # Add to workspace")

        input("\nPress Enter to execute...")

        print("\n[1/3] Executing: find div where role='button'")
        cmd = parser.parse('find div where role="button"')
        success, result = await executor.execute(cmd)
        role_buttons = [e for e in ctx.temp if e.attributes.get("role") == "button"]
        print(f"✓ Found {len(role_buttons)} div elements with role='button'")

        if len(role_buttons) > 0:
            print("\n[2/3] Executing: list temp")
            cmd = parser.parse("list temp")
            success, result = await executor.execute(cmd)
            print(f"\n{result[:300]}...")

            print("\n[3/3] Executing: add from temp")
            cmd = parser.parse("add from temp")
            success, result = await executor.execute(cmd)
            print(f"✓ Added {result} elements to workspace")

        input("\nPress Enter to continue to Demo 3...")

        # Demo 3: Refinement chain
        print("\n" + "=" * 70)
        print("Demo 3: Refinement chain (.find syntax)")
        print("=" * 70)
        print("Commands:")
        print("  1. find div                # Find all divs")
        print("  2. .find where visible     # Refine to visible only")
        print("  3. .find where enabled     # Further refine to enabled")

        input("\nPress Enter to execute...")

        print("\n[1/3] Executing: find div")
        cmd = parser.parse("find div")
        success, result = await executor.execute(cmd)
        all_divs = len(ctx.temp)
        print(f"✓ Found {all_divs} divs")

        print("\n[2/3] Executing: .find where visible")
        cmd = parser.parse(".find where visible")
        success, result = await executor.execute(cmd)
        visible_divs = len(ctx.temp)
        print(f"✓ Refined to {visible_divs} visible divs")
        print(f"  Filtered out {all_divs - visible_divs} hidden divs")

        print("\n[3/3] Executing: .find where enabled")
        cmd = parser.parse(".find where enabled")
        success, result = await executor.execute(cmd)
        enabled_divs = len(ctx.temp)
        print(f"✓ Refined to {enabled_divs} enabled divs")
        print(f"  Filtered out {visible_divs - enabled_divs} disabled divs")

        input("\nPress Enter to continue to Demo 4...")

        # Demo 4: Preview
        print("\n" + "=" * 70)
        print("Demo 4: Preview / Highlight elements in browser")
        print("=" * 70)
        print("Commands:")
        print("  1. preview workspace  # Highlight workspace elements")

        input("\nPress Enter to execute...")

        print("\n[1/1] Executing: preview workspace")
        cmd = parser.parse("preview workspace")
        success, result = await executor.execute(cmd)
        print(f"✓ {result}")
        print("\n✓ Look at the browser! Elements should be highlighted in blue.")

        input("\nPress Enter to continue...")

        # Demo 5: Show workspace
        print("\n" + "=" * 70)
        print("Demo 5: Three-layer state")
        print("=" * 70)
        print("Current state:")
        print(f"  • candidates: {len(ctx.candidates)} elements")
        print(f"  • temp: {len(ctx.temp)} elements")
        print(f"  • workspace: {len(ctx.workspace)} elements")

        print("\nCommands:")
        print("  1. list candidates  # Show candidates")
        print("  2. list temp        # Show temp")
        print("  3. list             # Show workspace (default)")

        input("\nPress Enter to execute...")

        print("\n[1/3] Executing: list candidates")
        cmd = parser.parse("list candidates")
        success, result = await executor.execute(cmd)
        print(f"\n{result[:200]}...")

        print("\n[2/3] Executing: list temp")
        cmd = parser.parse("list temp")
        success, result = await executor.execute(cmd)
        print(f"\n{result[:200]}...")

        print("\n[3/3] Executing: list")
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        print(f"\n{result}")

        print("\n" + "=" * 70)
        print("Demo Complete!")
        print("=" * 70)
        print("\nSummary:")
        print(f"  ✓ Scanned page and found {len(ctx.candidates)} elements")
        print(f"  ✓ Added {len(ctx.workspace)} elements to workspace")
        if role_buttons:
            print(f"  ✓ Found {len(role_buttons)} role='button' elements")
        print(f"  ✓ Refined results from {all_divs} → {visible_divs} → {enabled_divs}")
        print("  ✓ Previewed elements in browser")
        print("\nV2 three-layer architecture is working!")
        print("=" * 70)

    finally:
        await browser.close()


if __name__ == "__main__":
    print("Running V2 Demo...")
    asyncio.run(demo())
