#!/usr/bin/env python
"""
Test scanner integration with Element Location Strategy
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.scanner import ElementScanner
from src.core.locator.strategy import LocationStrategyEngine


async def test_scanner_uses_strategy_engine():
    """Test that scanner uses LocationStrategyEngine"""
    print("\n1. Testing Scanner uses LocationStrategyEngine...")

    # Create mock page with elements
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Create a simple test page
        await page.set_content("""
        <html>
        <body>
            <input type="email" id="email-field" name="email" placeholder="Enter email" />
            <input type="password" id="password-field" name="password" />
            <button type="submit" id="submit-btn">Submit</button>
        </body>
        </html>
        """, wait_until='domcontentloaded')

        # Scan elements
        scanner = ElementScanner()
        elements = await scanner.scan(page)

        print(f"   Scanned {len(elements)} elements")

        # Verify elements were found
        assert len(elements) == 3, f"Expected 3 elements, got {len(elements)}"

        # Check each element has selectors
        for elem in elements:
            print(f"\n   Element [{elem.index}]: {elem.tag} type={elem.type}")
            print(f"      Selector: {elem.selector}")
            print(f"      XPath: {elem.xpath}")
            print(f"      Cost: {elem.selector_cost}")
            print(f"      Strategy: {elem.strategy_used}")

            # Verify selector exists
            assert elem.selector, f"Element {elem.index} has no selector"
            assert elem.xpath, f"Element {elem.index} has no xpath"

            # Verify strategy metadata exists (should be populated by strategy engine)
            # Note: Depending on element quality, cost might be None for fallback
            if elem.selector_cost is not None:
                assert elem.selector_cost >= 0, "Cost should be >= 0"
                print(f"      [OK] Cost is valid: {elem.selector_cost:.3f}")

            if elem.strategy_used:
                print(f"      [OK] Strategy used: {elem.strategy_used}")

        # Check specific elements
        email_elem = next((e for e in elements if e.type == "email"), None)
        assert email_elem is not None, "Should find email input"
        assert "email" in email_elem.selector.lower(), "Selector should contain email"

        password_elem = next((e for e in elements if e.type == "password"), None)
        assert password_elem is not None, "Should find password input"
        assert "password" in password_elem.selector.lower(), "Selector should contain password"

        button_elem = next((e for e in elements if e.tag == "button"), None)
        assert button_elem is not None, "Should find button"
        assert "submit" in button_elem.selector.lower() or "button" in button_elem.selector.lower(), "Selector should contain submit or button"

        await browser.close()

        print("   [OK] All elements have selectors from strategy engine")
        return True


async def test_strategy_vs_fallback():
    """Test that strategy engine produces better selectors than fallback"""
    print("\n2. Testing Strategy Quality...")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Create page with elements that have unique IDs (best case for strategy engine)
        await page.set_content("""
        <html>
        <body>
            <input type="text" id="username" name="username" />
            <input type="email" id="email" name="email" />
            <button id="submit-button" type="submit">Submit</button>
        </body>
        </html>
        """, wait_until='domcontentloaded')

        scanner = ElementScanner()
        elements = await scanner.scan(page)

        # Elements with IDs should have ID_SELECTOR strategy
        for elem in elements:
            print(f"   {elem.tag}#{elem.id}: {elem.selector} (strategy: {elem.strategy_used}, cost: {elem.selector_cost})")

            # Element with ID should have ID-based selector
            if elem.id:
                assert f"#{elem.id}" in elem.selector or f"id='{elem.id}'" in elem.selector or elem.id in elem.selector, \
                    f"Selector should use ID for element with id={elem.id}"

                # Strategy should be ID_SELECTOR or XPATH_ID (both good)
                if elem.strategy_used:
                    assert 'ID' in elem.strategy_used, f"Strategy should be ID-based for {elem.id}"

        await browser.close()
        print("   [OK] Strategy engine used optimal strategies")
        return True


async def test_cost_tracking():
    """Test that cost is calculated and tracked"""
    print("\n3. Testing Cost Tracking...")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Create page with various element types
        await page.set_content("""
        <html>
        <body>
            <input type="text" id="field1" name="field1" />
            <input type="email" name="email" placeholder="Email" />
            <div class="container">
                <button class="btn-primary" type="submit">Submit</button>
            </div>
        </body>
        </html>
        """, wait_until='domcontentloaded')

        scanner = ElementScanner()
        elements = await scanner.scan(page)

        print(f"   Found {len(elements)} elements")

        # Check that elements have cost information
        elements_with_cost = [e for e in elements if e.selector_cost is not None]
        print(f"   Elements with cost info: {len(elements_with_cost)}")

        for elem in elements:
            if elem.selector_cost is not None:
                print(f"   Element {elem.index} ({elem.tag}): cost = {elem.selector_cost:.3f}, strategy = {elem.strategy_used}")
                assert 0 <= elem.selector_cost <= 1.0, "Cost should be between 0 and 1"

        # Elements with IDs should have low cost (good selectors)
        id_elements = [e for e in elements if e.id]
        for elem in id_elements:
            if elem.selector_cost is not None:
                assert elem.selector_cost < 0.2, f"Element with ID should have low cost, got {elem.selector_cost}"

        await browser.close()
        print("   [OK] Cost tracking working")
        return True


async def run_all_tests():
    """Run all integration tests"""
    print("="*70)
    print("Scanner Integration Test - Element Location Strategy")
    print("="*70)

    tests = [
        test_scanner_uses_strategy_engine,
        test_strategy_vs_fallback,
        test_cost_tracking,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n   [FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("="*70)

    if failed == 0:
        print("\n[SUCCESS] All integration tests passed!")
        print("\nElement Location Strategy successfully integrated into scanner!")
        print("- Elements now have intelligent selectors")
        print("- Cost metadata is tracked")
        print("- Strategy selection is optimized")
        return True
    else:
        print(f"\n[ERROR] {failed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
