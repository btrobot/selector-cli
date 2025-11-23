#!/usr/bin/env python
"""
Real Browser Testing Script for Phase 3
Tests the locator strategy engine with actual websites
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from playwright.async_api import async_playwright
from src.core.locator.scanner_integration import LocatorIntegrationEngine
from src.core.scanner.element_scanner import ElementScanner


async def test_simple_form():
    """Test on a simple HTML form"""
    print("\n" + "="*60)
    print("Test 1: Simple Form (Local HTML)")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Create a simple form
        await page.set_content("""
        <html>
        <body>
          <form>
            <input type='email' id='email' placeholder='Email'>
            <input type='password' id='password' placeholder='Password'>
            <button type='submit'>Login</button>
          </form>
        </body>
        </html>
        """)

        # Scan elements
        scanner = ElementScanner()
        elements = await scanner.scan(page)

        print(f"Found {len(elements)} elements")
        for i, elem in enumerate(elements):
            print(f"  [{i}] {elem}")

        # Process with locator engine
        engine = LocatorIntegrationEngine()
        results = await engine.process_collection(elements, page)

        await browser.close()

        return results


async def test_github_login():
    """Test on GitHub login page"""
    print("\n" + "="*60)
    print("Test 2: GitHub Login Page")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto('https://github.com/login')

        # Wait for form to load
        await page.wait_for_selector('input[name="login"]')

        # Scan elements
        scanner = ElementScanner()
        elements = await scanner.scan(page)

        print(f"Found {len(elements)} elements")

        # Process interactive elements only
        interactive = [e for e in elements if e.tag in ['input', 'button', 'a']]
        print(f"Processing {len(interactive)} interactive elements")

        engine = LocatorIntegrationEngine()
        results = await engine.process_collection(interactive[:10], page)  # Limit to 10 for speed

        await browser.close()

        return results


async def test_google_search():
    """Test on Google search page"""
    print("\n" + "="*60)
    print("Test 3: Google Search")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto('https://www.google.com')

        # Find search box
        search_box = await page.wait_for_selector('input[name="q"]')

        # Scan the page
        scanner = ElementScanner()
        elements = await scanner.scan(page)

        # Focus on form elements
        form_elements = [e for e in elements if e.tag in ['input', 'button']]
        print(f"Found {len(form_elements)} form elements")

        engine = LocatorIntegrationEngine()
        results = await engine.process_collection(form_elements[:8], page)

        await browser.close()

        return results


async def run_all_tests():
    """Run all real browser tests"""
    print("="*60)
    print("Phase 3 - Real Browser Testing")
    print("="*60)

    tests = [
        ("Simple Form", test_simple_form),
        ("GitHub Login", test_github_login),
        ("Google Search", test_google_search),
    ]

    all_results = {}

    for test_name, test_func in tests:
        try:
            results = await test_func()
            all_results[test_name] = results
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed: {e}")
            import traceback
            traceback.print_exc()
            all_results[test_name] = None

    # Print final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)

    for test_name, results in all_results.items():
        if results:
            print(f"\n{test_name}:")
            if 'stats' in results:
                stats = results['stats']
                print(f"  Elements: {stats['total_elements']}")
                print(f"  Success: {stats['successful']} ({stats['successful']/stats['total_elements']*100:.1f}%)")
                print(f"  Failed: {stats['failed']}")

                if stats['by_strategy']:
                    print(f"  Top strategies:")
                    for strategy, count in list(stats['by_strategy'].items())[:3]:
                        print(f"    - {strategy}: {count}")
            else:
                print(f"  Results: {len(results.get('results', []))} elements processed")
        else:
            print(f"\n{test_name}: FAILED")

    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

    return all_results


if __name__ == '__main__':
    results = asyncio.run(run_all_tests())
    sys.exit(0 if all(r is not None for r in results.values()) else 1)
