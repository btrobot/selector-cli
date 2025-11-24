"""
Simple integration tests for V2 - Manual run script
Run with: python tests/test_v2_integration_simple.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from selector_cli.core.browser import BrowserManager
from selector_cli.core.context_v2 import ContextV2
from selector_cli.parser.parser_v2 import ParserV2
from selector_cli.commands.executor_v2 import ExecutorV2


async def test_scan_add_list():
    """Test: scan -> add button -> list"""
    print("\n=== Test: scan -> add button -> list ===")

    # Setup
    ctx = ContextV2(enable_history_file=False)
    parser = ParserV2()
    executor = ExecutorV2(ctx)

    browser = BrowserManager()
    await browser.initialize(headless=True)
    ctx.browser = browser

    try:
        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url
        print(f"Loaded: {test_url}")

        # Step 1: scan
        print("\n1. Executing: scan")
        cmd = parser.parse("scan")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Candidates found: {len(ctx.candidates)}")
        assert success
        assert len(ctx.candidates) > 0

        # Step 2: add button
        print("\n2. Executing: add button")
        cmd = parser.parse("add button")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Buttons added: {result}")
        print(f"   Workspace count: {len(ctx.workspace)}")
        assert success
        assert result > 0

        # Step 3: list
        print("\n3. Executing: list")
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Output preview:\n{result[:200]}...")
        assert success
        assert "workspace" in result

        print("\n✓ Test passed!")

    finally:
        await browser.close()


async def test_find_role_button():
    """Test: find div where role='button' -> list temp -> add from temp"""
    print("\n=== Test: find div where role='button' -> list temp -> add from temp ===")

    # Setup
    ctx = ContextV2(enable_history_file=False)
    parser = ParserV2()
    executor = ExecutorV2(ctx)

    browser = BrowserManager()
    await browser.initialize(headless=True)
    ctx.browser = browser

    try:
        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url
        print(f"Loaded: {test_url}")

        # Initial scan and add traditional buttons
        print("\n1. Executing: scan")
        cmd = parser.parse("scan")
        await executor.execute(cmd)
        print(f"   Candidates: {len(ctx.candidates)}")

        print("\n2. Executing: add button")
        cmd = parser.parse("add button")
        await executor.execute(cmd)
        print(f"   Workspace after adding buttons: {len(ctx.workspace)}")

        # Step 1: find div where role="button"
        print("\n3. Executing: find div where role='button'")
        cmd = parser.parse('find div where role="button"')
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Role buttons found: {len(ctx.temp)}")
        assert success

        if len(ctx.temp) > 0:
            # Verify they have role=button
            role_buttons = [e for e in ctx.temp if e.attributes.get("role") == "button"]
            print(f"   Confirmed role='button': {len(role_buttons)}")

            # Step 2: list temp
            print("\n4. Executing: list temp")
            cmd = parser.parse("list temp")
            success, result = await executor.execute(cmd)
            print(f"   Success: {success}")
            print(f"   Output contains 'temp': {'temp' in result}")
            assert success
            assert "temp" in result

            # Step 3: add from temp
            print("\n5. Executing: add from temp")
            cmd = parser.parse("add from temp")
            success, result = await executor.execute(cmd)
            print(f"   Success: {success}")
            print(f"   Added from temp: {result}")
            print(f"   Final workspace count: {len(ctx.workspace)}")
            assert success
            assert result == len(role_buttons)

            print("\n✓ Test passed! Found and added role='button' elements")
        else:
            print("\n⚠ No role='button' elements found (may be expected)")

    finally:
        await browser.close()


async def test_chain_refine():
    """Test: find div -> .find where visible -> .find where enabled"""
    print("\n=== Test: find div -> .find where visible -> .find where enabled ===")

    # Setup
    ctx = ContextV2(enable_history_file=False)
    parser = ParserV2()
    executor = ExecutorV2(ctx)

    browser = BrowserManager()
    await browser.initialize(headless=True)
    ctx.browser = browser

    try:
        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url
        print(f"Loaded: {test_url}")

        # Step 1: find div
        print("\n1. Executing: find div")
        cmd = parser.parse("find div")
        success, result = await executor.execute(cmd)
        initial_count = len(ctx.temp)
        print(f"   Success: {success}")
        print(f"   All divs: {initial_count}")
        assert success
        assert initial_count > 0

        # Step 2: .find where visible
        print("\n2. Executing: .find where visible")
        cmd = parser.parse(".find where visible")
        success, result = await executor.execute(cmd)
        visible_count = len(ctx.temp)
        print(f"   Success: {success}")
        print(f"   Visible divs: {visible_count}")
        assert success
        assert visible_count <= initial_count

        # Step 3: .find where enabled
        print("\n3. Executing: .find where enabled")
        cmd = parser.parse(".find where enabled")
        success, result = await executor.execute(cmd)
        enabled_count = len(ctx.temp)
        print(f"   Success: {success}")
        print(f"   Enabled divs: {enabled_count}")
        assert success
        assert enabled_count <= visible_count

        # Verify all results are enabled and visible
        for elem in ctx.temp:
            assert elem.visible is True
            assert elem.enabled is True

        print("\n✓ Test passed! Refinement chain worked correctly")

    finally:
        await browser.close()


async def test_list_different_sources():
    """Test: list candidates, list temp, list workspace"""
    print("\n=== Test: list candidates, list temp, list workspace ===")

    # Setup
    ctx = ContextV2(enable_history_file=False)
    parser = ParserV2()
    executor = ExecutorV2(ctx)

    browser = BrowserManager()
    await browser.initialize(headless=True)
    ctx.browser = browser

    try:
        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url
        print(f"Loaded: {test_url}")

        # Populate different layers
        cmd = parser.parse("scan")
        await executor.execute(cmd)
        print(f"\n1. Scanned - Candidates: {len(ctx.candidates)}")

        cmd = parser.parse("add button")
        await executor.execute(cmd)
        print(f"2. Added buttons - Workspace: {len(ctx.workspace)}")

        cmd = parser.parse("find div")
        await executor.execute(cmd)
        print(f"3. Found divs - Temp: {len(ctx.temp)}")

        # List candidates
        print("\n4. Executing: list candidates")
        cmd = parser.parse("list candidates")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Output contains 'candidates': {'candidates' in result}")
        assert success

        # List temp
        print("\n5. Executing: list temp")
        cmd = parser.parse("list temp")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Output contains 'temp': {'temp' in result}")
        assert success

        # List workspace (default)
        print("\n6. Executing: list")
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        print(f"   Success: {success}")
        print(f"   Output contains 'workspace': {'workspace' in result}")
        assert success

        print("\n✓ Test passed!")

    finally:
        await browser.close()


async def main():
    """Run all integration tests"""
    print("=" * 70)
    print("V2 Integration Tests")
    print("=" * 70)

    tests = [
        test_scan_add_list,
        test_find_role_button,
        test_chain_refine,
        test_list_different_sources,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
