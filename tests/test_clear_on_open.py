"""
Test: Verify that opening a new page clears elements and collection
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

import asyncio
from src.repl.main import SelectorREPL
from src.core.browser import BrowserManager

async def test_clear_on_new_page():
    """Test that opening new page clears old elements"""

    # Get local test page path
    test_page = Path(__file__).parent.parent.parent / 'selector-explorer' / 'test_page.html'

    if not test_page.exists():
        print("[SKIP] Test page not found")
        return

    test_url = f'file:///{test_page.absolute().as_posix()}'

    print("="*60)
    print("Test: Clear Elements on New Page")
    print("="*60)

    repl = SelectorREPL()
    repl.context.browser = BrowserManager()
    await repl.context.browser.initialize(headless=True)

    # Step 1: Open first page and scan
    print("\n1. Open first page and scan")
    cmd = repl.parser.parse(f"open {test_url}")
    result = await repl.executor.execute(cmd, repl.context)
    print(f"   {result}")

    cmd = repl.parser.parse("scan")
    result = await repl.executor.execute(cmd, repl.context)
    print(f"   {result}")

    # Step 2: Add elements to collection
    print("\n2. Add elements to collection")
    cmd = repl.parser.parse("add input")
    result = await repl.executor.execute(cmd, repl.context)
    print(f"   {result}")

    # Verify we have elements
    elements_count = len(repl.context.all_elements)
    collection_count = repl.context.collection.count()
    print(f"   Elements scanned: {elements_count}")
    print(f"   Collection size: {collection_count}")

    assert elements_count > 0, "Should have scanned elements"
    assert collection_count > 0, "Should have collection elements"

    # Step 3: Open a new page (same page, but should clear)
    print("\n3. Open new page (should clear elements and collection)")
    cmd = repl.parser.parse(f"open {test_url}")
    result = await repl.executor.execute(cmd, repl.context)
    print(f"   {result}")

    # Verify elements and collection are cleared
    elements_after = len(repl.context.all_elements)
    collection_after = repl.context.collection.count()
    scan_time_after = repl.context.last_scan_time

    print(f"   Elements after open: {elements_after}")
    print(f"   Collection after open: {collection_after}")
    print(f"   Last scan time: {scan_time_after}")

    assert elements_after == 0, f"Elements should be cleared, but found {elements_after}"
    assert collection_after == 0, f"Collection should be cleared, but found {collection_after}"
    assert scan_time_after is None, "Scan time should be reset"

    print("\n[OK] Elements and collection successfully cleared on new page!")

    # Step 4: Scan again to verify we can still scan
    print("\n4. Scan new page to verify functionality")
    cmd = repl.parser.parse("scan")
    result = await repl.executor.execute(cmd, repl.context)
    print(f"   {result}")

    elements_final = len(repl.context.all_elements)
    print(f"   Elements after scan: {elements_final}")

    assert elements_final > 0, "Should be able to scan new page"

    print("\n[OK] Can successfully scan after opening new page!")

    # Cleanup
    await repl.context.browser.close()

    print("\n" + "="*60)
    print("[OK] Test passed! New page clears old elements.")
    print("="*60)

if __name__ == '__main__':
    asyncio.run(test_clear_on_new_page())
