"""
Test Phase 3 - Code generation and export
"""
import sys
import os
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.parser import Parser
from src.commands.executor import CommandExecutor
from src.core.element import Element
from src.generators import (
    PlaywrightGenerator, SeleniumGenerator, PuppeteerGenerator,
    JSONExporter, CSVExporter, YAMLExporter
)


def create_test_elements():
    """Create test elements"""
    return [
        Element(
            index=0,
            uuid="elem-0",
            tag="input",
            selector='input[type="email"]',
            type="email",
            id="email",
            name="user_email",
            placeholder="Enter email",
            text="",
            attributes={"type": "email", "id": "email"}
        ),
        Element(
            index=1,
            uuid="elem-1",
            tag="input",
            selector='input[type="password"]',
            type="password",
            id="password",
            name="user_password",
            placeholder="",
            text="",
            attributes={"type": "password", "id": "password"}
        ),
        Element(
            index=2,
            uuid="elem-2",
            tag="button",
            selector='button[type="submit"]',
            type="submit",
            id="submit-btn",
            name="",
            placeholder="",
            text="Login",
            attributes={"type": "submit", "id": "submit-btn"}
        ),
    ]


def test_export_command_parsing():
    """Test export command parsing"""
    print("\n" + "="*60)
    print("Testing Export Command Parsing")
    print("="*60)

    parser = Parser()

    tests = [
        ("export playwright", "playwright", None),
        ("export selenium", "selenium", None),
        ("export puppeteer", "puppeteer", None),
        ("export json", "json", None),
        ("export csv", "csv", None),
        ("export yaml", "yaml", None),
        ("export playwright > test.py", "playwright", "test.py"),
        ("export json > data.json", "json", "data.json"),
    ]

    for test_input, expected_format, expected_file in tests:
        print(f"\nInput: {test_input}")
        cmd = parser.parse(test_input)

        assert cmd.verb == "export", f"Expected verb 'export', got {cmd.verb}"
        assert cmd.argument is not None, "Expected argument"

        # Parse argument
        parts = cmd.argument.split(':', 1)
        actual_format = parts[0]
        actual_file = parts[1] if len(parts) > 1 else None

        assert actual_format == expected_format, f"Expected format '{expected_format}', got '{actual_format}'"
        assert actual_file == expected_file, f"Expected file '{expected_file}', got '{actual_file}'"

        print(f"  [OK] Format: {actual_format}")
        if actual_file:
            print(f"  [OK] File: {actual_file}")

    print("\n[OK] Export command parsing tests passed")
    return True


def test_playwright_generator():
    """Test Playwright code generation"""
    print("\n" + "="*60)
    print("Testing Playwright Generator")
    print("="*60)

    generator = PlaywrightGenerator()
    elements = create_test_elements()
    url = "https://example.com/login"

    code = generator.generate(elements, url)

    print(f"\nGenerated code ({len(code)} chars):")
    print("-" * 40)
    print(code[:500])  # Print first 500 chars
    print("-" * 40)

    # Verify key components
    assert "from playwright.sync_api import sync_playwright" in code
    assert "page.goto('https://example.com/login')" in code
    assert "page.locator" in code
    assert len(code) > 100

    print("\n[OK] Playwright generator works correctly")
    return True


def test_selenium_generator():
    """Test Selenium code generation"""
    print("\n" + "="*60)
    print("Testing Selenium Generator")
    print("="*60)

    generator = SeleniumGenerator()
    elements = create_test_elements()
    url = "https://example.com/login"

    code = generator.generate(elements, url)

    print(f"\nGenerated code ({len(code)} chars):")
    print("-" * 40)
    print(code[:500])
    print("-" * 40)

    # Verify key components
    assert "from selenium import webdriver" in code
    assert "driver.get('https://example.com/login')" in code
    assert "find_element" in code

    print("\n[OK] Selenium generator works correctly")
    return True


def test_puppeteer_generator():
    """Test Puppeteer code generation"""
    print("\n" + "="*60)
    print("Testing Puppeteer Generator")
    print("="*60)

    generator = PuppeteerGenerator()
    elements = create_test_elements()
    url = "https://example.com/login"

    code = generator.generate(elements, url)

    print(f"\nGenerated code ({len(code)} chars):")
    print("-" * 40)
    print(code[:500])
    print("-" * 40)

    # Verify key components
    assert "const puppeteer = require('puppeteer')" in code
    assert "await page.goto('https://example.com/login')" in code
    assert "await page.$(" in code  # Single element selector

    print("\n[OK] Puppeteer generator works correctly")
    return True


def test_json_exporter():
    """Test JSON export"""
    print("\n" + "="*60)
    print("Testing JSON Exporter")
    print("="*60)

    exporter = JSONExporter()
    elements = create_test_elements()

    output = exporter.generate(elements)

    print(f"\nGenerated JSON ({len(output)} chars):")
    print("-" * 40)
    print(output[:500])
    print("-" * 40)

    # Verify it's valid JSON
    import json
    data = json.loads(output)
    assert len(data) == 3
    assert data[0]["tag"] == "input"
    assert data[0]["type"] == "email"

    print("\n[OK] JSON exporter works correctly")
    return True


def test_csv_exporter():
    """Test CSV export"""
    print("\n" + "="*60)
    print("Testing CSV Exporter")
    print("="*60)

    exporter = CSVExporter()
    elements = create_test_elements()

    output = exporter.generate(elements)

    print(f"\nGenerated CSV ({len(output)} chars):")
    print("-" * 40)
    print(output[:300])
    print("-" * 40)

    # Verify CSV structure
    lines = output.strip().split('\n')
    assert len(lines) >= 4  # Header + 3 elements
    assert "index,tag,type" in lines[0]

    print("\n[OK] CSV exporter works correctly")
    return True


def test_yaml_exporter():
    """Test YAML export"""
    print("\n" + "="*60)
    print("Testing YAML Exporter")
    print("="*60)

    exporter = YAMLExporter()
    elements = create_test_elements()

    output = exporter.generate(elements)

    print(f"\nGenerated YAML ({len(output)} chars):")
    print("-" * 40)
    print(output[:300])
    print("-" * 40)

    # Verify YAML structure
    assert "- index: 0" in output
    assert "tag: input" in output
    assert "type: email" in output

    print("\n[OK] YAML exporter works correctly")
    return True


def test_file_export():
    """Test file export functionality"""
    print("\n" + "="*60)
    print("Testing File Export")
    print("="*60)

    generator = JSONExporter()
    elements = create_test_elements()
    test_file = "test_export.json"

    # Generate and write to file
    output = generator.generate(elements)

    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(output)

        # Verify file exists and content is correct
        assert os.path.exists(test_file)

        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert len(content) > 0
        import json
        data = json.loads(content)
        assert len(data) == 3

        print(f"\n[OK] File '{test_file}' created successfully")
        print(f"[OK] File size: {len(content)} bytes")

    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"[OK] Test file cleaned up")

    print("\n[OK] File export works correctly")
    return True


if __name__ == '__main__':
    success = True
    success = test_export_command_parsing() and success
    success = test_playwright_generator() and success
    success = test_selenium_generator() and success
    success = test_puppeteer_generator() and success
    success = test_json_exporter() and success
    success = test_csv_exporter() and success
    success = test_yaml_exporter() and success
    success = test_file_export() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL PHASE 3 TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
