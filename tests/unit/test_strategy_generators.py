#!/usr/bin/env python
"""
Phase 4 - Strategy Generator Tests
Test all 17 strategy generators in strategy.py
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.strategy import LocationStrategyEngine
from src.core.element import Element


def create_element(**kwargs):
    """Create test element with default values"""
    defaults = {
        'index': 0,
        'uuid': 'test-uuid',
        'tag': 'input',
        'type': 'text',
        'id': '',
        'name': '',
        'placeholder': '',
        'text': '',
        'classes': [],
        'attributes': {}
    }
    defaults.update(kwargs)
    return Element(**defaults)


def test_id_selector_generator():
    """Test ID_SELECTOR strategy generator"""
    print("\n1. Testing ID_SELECTOR generator...")

    engine = LocationStrategyEngine()

    # Element with ID
    element = create_element(tag="button", id="submit-btn")
    selector = engine._generate_id_selector(element)
    assert selector == "#submit-btn", f"Expected '#submit-btn', got {selector}"
    print(f"   [OK] Generated: {selector}")

    # Element without ID
    element = create_element(tag="button", id="")
    selector = engine._generate_id_selector(element)
    assert selector is None, f"Expected None, got {selector}"
    print("   [OK] Returns None when no ID")

    return True


def test_data_testid_generator():
    """Test DATA_TESTID strategy generator"""
    print("\n2. Testing DATA_TESTID generator...")

    engine = LocationStrategyEngine()

    # Element with data-testid
    element = create_element(attributes={"data-testid": "submit-button"})
    selector = engine._generate_data_testid_selector(element)
    assert selector == '[data-testid="submit-button"]', f"Got {selector}"
    print(f"   [OK] Generated: {selector}")

    # Element without data-testid
    element = create_element(attributes={})
    selector = engine._generate_data_testid_selector(element)
    assert selector is None
    print("   [OK] Returns None when no data-testid")

    return True


def test_label_for_generator():
    """Test LABEL_FOR strategy generator"""
    print("\n3. Testing LABEL_FOR generator...")

    engine = LocationStrategyEngine()

    # Element with ID (for label[for])
    element = create_element(tag="input", id="email-field")
    selector = engine._generate_label_for_selector(element)
    assert 'label[for="email-field"]' in selector
    print(f"   [OK] Generated: {selector}")

    # Element without ID
    element = create_element(tag="input", id="")
    selector = engine._generate_label_for_selector(element)
    assert selector is None
    print("   [OK] Returns None when no ID")

    return True


def test_type_name_placeholder_generator():
    """Test TYPE_NAME_PLACEHOLDER generator"""
    print("\n4. Testing TYPE_NAME_PLACEHOLDER generator...")

    engine = LocationStrategyEngine()

    # Input with all three attributes
    element = create_element(
        tag="input",
        type="email",
        name="user-email",
        placeholder="Enter Email"
    )
    selector = engine._generate_type_name_placeholder_selector(element)
    assert 'type="email"' in selector
    assert 'name="user-email"' in selector
    assert 'placeholder="Enter Email"' in selector
    print(f"   [OK] Generated: {selector}")

    # Missing placeholder
    element = create_element(tag="input", type="email", name="user-email", placeholder="")
    selector = engine._generate_type_name_placeholder_selector(element)
    assert selector is None
    print("   [OK] Returns None when missing attributes")

    return True


def test_href_generator():
    """Test HREF strategy generator"""
    print("\n5. Testing HREF generator...")

    engine = LocationStrategyEngine()

    # Link with href
    element = create_element(tag="a", attributes={"href": "/login"})
    selector = engine._generate_href_selector(element)
    assert selector == 'a[href="/login"]'
    print(f"   [OK] Generated: {selector}")

    # Link without href
    element = create_element(tag="a", attributes={})
    selector = engine._generate_href_selector(element)
    assert selector is None
    print("   [OK] Returns None when no href")

    # Not a link
    element = create_element(tag="button", attributes={"href": "/login"})
    selector = engine._generate_href_selector(element)
    assert selector is None
    print("   [OK] Returns None for non-link elements")

    return True


def test_type_name_generator():
    """Test TYPE_NAME generator"""
    print("\n6. Testing TYPE_NAME generator...")

    engine = LocationStrategyEngine()

    # Input with type and name
    element = create_element(tag="input", type="email", name="user-email")
    selector = engine._generate_type_name_selector(element)
    assert 'type="email"' in selector
    assert 'name="user-email"' in selector
    print(f"   [OK] Generated: {selector}")

    # Missing name
    element = create_element(tag="input", type="email", name="")
    selector = engine._generate_type_name_selector(element)
    assert selector is None
    print("   [OK] Returns None when missing attributes")

    return True


def test_type_placeholder_generator():
    """Test TYPE_PLACEHOLDER generator"""
    print("\n7. Testing TYPE_PLACEHOLDER generator...")

    engine = LocationStrategyEngine()

    # Input with type and placeholder
    element = create_element(tag="input", type="email", placeholder="Enter Email")
    selector = engine._generate_type_placeholder_selector(element)
    assert 'type="email"' in selector
    assert 'placeholder="Enter Email"' in selector
    print(f"   [OK] Generated: {selector}")

    return True


def test_aria_label_generator():
    """Test ARIA_LABEL generator"""
    print("\n8. Testing ARIA_LABEL generator...")

    engine = LocationStrategyEngine()

    # Element with aria-label
    element = create_element(attributes={"aria-label": "Close dialog"})
    selector = engine._generate_aria_label_selector(element)
    assert selector == '[aria-label="Close dialog"]'
    print(f"   [OK] Generated: {selector}")

    return True


def test_title_attr_generator():
    """Test TITLE_ATTR generator"""
    print("\n9. Testing TITLE_ATTR generator...")

    engine = LocationStrategyEngine()

    # Element with title
    element = create_element(attributes={"title": "Submit form"})
    selector = engine._generate_title_attr_selector(element)
    assert selector == '[title="Submit form"]'
    print(f"   [OK] Generated: {selector}")

    return True


def test_class_unique_generator():
    """Test CLASS_UNIQUE generator"""
    print("\n10. Testing CLASS_UNIQUE generator...")

    engine = LocationStrategyEngine()

    # Element with single unique class
    element = create_element(classes=["btn-primary"])
    selector = engine._generate_class_unique_selector(element)
    assert selector == ".btn-primary"
    print(f"   [OK] Generated: {selector}")

    # Multiple classes - should return None
    element = create_element(classes=["btn", "btn-primary", "active"])
    selector = engine._generate_class_unique_selector(element)
    assert selector is None
    print("   [OK] Returns None for multiple classes")

    return True


def test_text_content_generator():
    """Test TEXT_CONTENT generator"""
    print("\n11. Testing TEXT_CONTENT generator...")

    engine = LocationStrategyEngine()

    # Button with text
    element = create_element(tag="button", text="Submit")
    selector = engine._generate_text_content_selector(element)
    assert 'Submit' in selector
    print(f"   [OK] Generated: {selector}")

    # Element without text
    element = create_element(tag="button", text="")
    selector = engine._generate_text_content_selector(element)
    assert selector is None
    print("   [OK] Returns None when no text")

    return True


def test_type_only_generator():
    """Test TYPE_ONLY generator"""
    print("\n12. Testing TYPE_ONLY generator...")

    engine = LocationStrategyEngine()

    # Input with type
    element = create_element(tag="input", type="email")
    selector = engine._generate_type_only_selector(element)
    assert selector == 'input[type="email"]'
    print(f"   [OK] Generated: {selector}")

    return True


def test_xpath_id_generator():
    """Test XPATH_ID generator"""
    print("\n13. Testing XPATH_ID generator...")

    engine = LocationStrategyEngine()

    # Element with ID
    element = create_element(tag="input", id="email-field")
    selector = engine._generate_xpath_id_selector(element)
    assert "@id='email-field'" in selector
    print(f"   [OK] Generated: {selector}")

    return True


def test_xpath_attr_generator():
    """Test XPATH_ATTR generator"""
    print("\n14. Testing XPATH_ATTR generator...")

    engine = LocationStrategyEngine()

    # Element with type and name
    element = create_element(tag="input", type="email", name="user-email")
    selector = engine._generate_xpath_attr_selector(element)
    assert "@type='email'" in selector
    assert "@name='user-email'" in selector
    print(f"   [OK] Generated: {selector}")

    return True


def test_xpath_text_generator():
    """Test XPATH_TEXT generator"""
    print("\n15. Testing XPATH_TEXT generator...")

    engine = LocationStrategyEngine()

    # Element with text
    element = create_element(tag="button", text="Submit")
    selector = engine._generate_xpath_text_selector(element)
    assert "contains(text()" in selector
    assert "Submit" in selector
    print(f"   [OK] Generated: {selector}")

    return True


def test_xpath_position_generator():
    """Test XPATH_POSITION generator"""
    print("\n16. Testing XPATH_POSITION generator...")

    engine = LocationStrategyEngine()

    element = create_element(tag="button")
    selector = engine._generate_xpath_position_selector(element)
    assert "button" in selector
    print(f"   [OK] Generated: {selector}")

    return True


def test_strategy_priorities():
    """Test that strategies are properly sorted by priority"""
    print("\n17. Testing strategy priority ordering...")

    engine = LocationStrategyEngine()

    # CSS strategies should be sorted by priority (ascending)
    prev_priority = 0
    for strategy in engine.css_strategies:
        current = strategy['priority'].value
        assert current >= prev_priority, f"Priority ordering broken: {current} < {prev_priority}"
        prev_priority = current

    print(f"   [OK] All {len(engine.css_strategies)} CSS strategies properly sorted")

    # XPath strategies should also be sorted
    prev_priority = 0
    for strategy in engine.xpath_strategies:
        current = strategy['priority'].value
        assert current >= prev_priority, f"Priority ordering broken: {current} < {prev_priority}"
        prev_priority = current

    print(f"   [OK] All {len(engine.xpath_strategies)} XPath strategies properly sorted")
    return True


def run_all_tests():
    """Run all strategy generator tests"""
    print("="*60)
    print("Phase 4 - Strategy Generator Tests")
    print("="*60)

    all_tests = [
        test_id_selector_generator,
        test_data_testid_generator,
        test_label_for_generator,
        test_type_name_placeholder_generator,
        test_href_generator,
        test_type_name_generator,
        test_type_placeholder_generator,
        test_aria_label_generator,
        test_title_attr_generator,
        test_class_unique_generator,
        test_text_content_generator,
        test_type_only_generator,
        test_xpath_id_generator,
        test_xpath_attr_generator,
        test_xpath_text_generator,
        test_xpath_position_generator,
        test_strategy_priorities,
    ]

    passed = 0
    failed = 0

    for test in all_tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   [FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n[PASS] ALL STRATEGY TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed} GENERATOR TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
