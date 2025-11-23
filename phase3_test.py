#!/usr/bin/env python
"""
Test Phase 3 Export Functionality
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.generators import (
    PlaywrightGenerator,
    SeleniumGenerator,
    PuppeteerGenerator,
    JSONExporter,
    CSVExporter,
    YAMLExporter
)
from src.core.element import Element


def create_test_element(**kwargs):
    """Create test element for export testing"""
    defaults = {
        'index': 0,
        'uuid': 'test-uuid-123',
        'tag': 'input',
        'type': 'email',
        'id': 'email-field',
        'name': 'email',
        'placeholder': 'Enter email',
        'text': '',
        'classes': [],
        'attributes': {'type': 'email', 'id': 'email-field', 'name': 'email'},
        'selector': 'input[type="email"][id="email-field"]',
        'xpath': "//input[@id='email-field']",
        'visible': True,
        'enabled': True,
        'disabled': False,
    }
    defaults.update(kwargs)
    return Element(**defaults)


async def test_playwright_generator():
    """Test Playwright code generation"""
    print("\n1. Testing Playwright Generator...")

    generator = PlaywrightGenerator()

    elements = [
        create_test_element(index=0, type="email", id="email-input", name="email"),
        create_test_element(index=1, type="password", id="password-input", name="password"),
        create_test_element(index=2, tag="button", type="submit", id="submit-btn", text="Submit"),
    ]

    code = generator.generate(elements, url="https://example.com/login")

    # Verify code contains key elements
    assert "from playwright.sync_api import sync_playwright" in code
    assert "browser = p.chromium.launch" in code
    assert "email = page.locator" in code
    assert "password = page.locator" in code
    assert "submit = page.locator" in code

    print("   ✅ Playwright code generated successfully")
    print(f"   📄 Generated {len(code)} characters of code")

    return True


async def test_selenium_generator():
    """Test Selenium code generation"""
    print("\n2. Testing Selenium Generator...")

    from src.generators.selenium_gen import SeleniumGenerator

    generator = SeleniumGenerator()

    elements = [
        create_test_element(index=0, type="email", id="email-input"),
        create_test_element(index=1, type="password", id="password-input"),
    ]

    code = generator.generate(elements, url="https://example.com/login")

    assert "from selenium import webdriver" in code
    assert "from selenium.webdriver.common.by import By" in code
    assert '.find_element(By.CSS_SELECTOR' in code

    print("   ✅ Selenium code generated successfully")

    return True


async def test_json_export():
    """Test JSON export"""
    print("\n3. Testing JSON Exporter...")

    exporter = JSONExporter()

    elements = [
        create_test_element(index=0, type="email", id="email-input"),
        create_test_element(index=1, type="password", id="password-input"),
    ]

    output = exporter.generate(elements)

    import json
    data = json.loads(output)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['tag'] == 'input'
    assert data[0]['type'] == 'email'
    assert 'selector' in data[0]

    print("   ✅ JSON export successful")
    print(f"   📄 Exported {len(data)} elements")

    return True


async def test_csv_export():
    """Test CSV export"""
    print("\n4. Testing CSV Exporter...")

    exporter = CSVExporter()

    elements = [
        create_test_element(index=0, type="email"),
        create_test_element(index=1, type="password"),
    ]

    output = exporter.generate(elements)

    assert "index,tag,type," in output
    assert "email" in output
    assert "password" in output

    print("   ✅ CSV export successful")

    return True


async def test_yaml_export():
    """Test YAML export"""
    print("\n5. Testing YAML Exporter...")

    exporter = YAMLExporter()

    elements = [
        create_test_element(index=0, type="email"),
    ]

    output = exporter.generate(elements)

    assert "- index: 0" in output
    assert "tag: input" in output
    assert "type: email" in output

    print("   ✅ YAML export successful")

    return True


async def test_all_generators():
    """Test all generators"""
    print("\n6. Testing All Generators...")

    generators = [
        ("Playwright", PlaywrightGenerator()),
        ("Selenium", SeleniumGenerator()),
        ("Puppeteer", PuppeteerGenerator()),
        ("JSON", JSONExporter()),
        ("CSV", CSVExporter()),
        ("YAML", YAMLExporter()),
    ]

    elements = [
        create_test_element(index=0, type="email"),
        create_test_element(index=1, type="password"),
        create_test_element(index=2, tag="button", type="submit", text="Login"),
    ]

    for name, generator in generators:
        try:
            output = generator.generate(elements, url="https://example.com")
            assert len(output) > 0, f"{name} generated empty output"
            print(f"   ✅ {name:12s} - OK ({len(output)} chars)")
        except Exception as e:
            print(f"   ❌ {name:12s} - FAILED: {e}")
            return False

    return True


async def run_all_tests():
    """Run all Phase 3 tests"""
    print("="*60)
    print("Phase 3 - Code Generation Tests")
    print("="*60)

    tests = [
        test_playwright_generator,
        test_selenium_generator,
        test_json_export,
        test_csv_export,
        test_yaml_export,
        test_all_generators,
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
            print(f"\n   ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("="*60)

    if failed == 0:
        print("\n🎉 All Phase 3 generator tests passed!")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
