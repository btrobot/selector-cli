#!/usr/bin/env python
"""
Test Phase 2 CSS strategies
Verifies that the 5 new CSS strategies work correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.strategy import LocationStrategyEngine
from src.core.element import Element


def test_aria_label_strategy():
    """Test ARIA_LABEL strategy"""
    print("\n1. Testing ARIA_LABEL strategy...")

    engine = LocationStrategyEngine()
    element = Element(
        index=0,
        uuid='test-uuid',
        tag='button',
        attributes={'aria-label': 'Submit form'}
    )

    selector = engine._generate_aria_label_selector(element)
    expected = '[aria-label="Submit form"]'

    if selector == expected:
        print(f"   [OK] Generated: {selector}")
        return True
    else:
        print(f"   [FAIL] Expected: {expected}, Got: {selector}")
        return False


def test_title_attr_strategy():
    """Test TITLE_ATTR strategy"""
    print("\n2. Testing TITLE_ATTR strategy...")

    engine = LocationStrategyEngine()
    element = Element(
        index=0,
        uuid='test-uuid',
        tag='input',
        attributes={'title': 'Email address field'}
    )

    selector = engine._generate_title_attr_selector(element)
    expected = '[title="Email address field"]'

    if selector == expected:
        print(f"   [OK] Generated: {selector}")
        return True
    else:
        print(f"   [FAIL] Expected: {expected}, Got: {selector}")
        return False


def test_class_unique_strategy():
    """Test CLASS_UNIQUE strategy"""
    print("\n3. Testing CLASS_UNIQUE strategy...")

    engine = LocationStrategyEngine()

    # Test with single class
    element1 = Element(
        index=0,
        uuid='test-uuid',
        tag='div',
        classes=['submit-button']
    )

    selector1 = engine._generate_class_unique_selector(element1)
    expected1 = '.submit-button'

    success1 = selector1 == expected1
    if success1:
        print(f"   [OK] Single class: {selector1}")
    else:
        print(f"   [FAIL] Expected: {expected1}, Got: {selector1}")

    # Test with multiple classes (should return None)
    element2 = Element(
        index=0,
        uuid='test-uuid',
        tag='div',
        classes=['btn', 'primary', 'large']
    )

    selector2 = engine._generate_class_unique_selector(element2)
    success2 = selector2 is None

    if success2:
        print(f"   [OK] Multiple classes correctly returns None")
    else:
        print(f"   [FAIL] Multiple classes should return None, got: {selector2}")

    # Test with no classes (should return None)
    element3 = Element(
        index=0,
        uuid='test-uuid',
        tag='div',
        classes=[]
    )

    selector3 = engine._generate_class_unique_selector(element3)
    success3 = selector3 is None

    if success3:
        print(f"   [OK] No classes correctly returns None")
    else:
        print(f"   [FAIL] No classes should return None, got: {selector3}")

    return success1 and success2 and success3


def test_nth_of_type_strategy():
    """Test NTH_OF_TYPE strategy"""
    print("\n4. Testing NTH_OF_TYPE strategy...")

    engine = LocationStrategyEngine()
    element = Element(
        index=0,
        uuid='test-uuid',
        tag='button'
    )

    selector = engine._generate_nth_of_type_selector(element)
    expected = 'button:nth-of-type(1)'

    if selector == expected:
        print(f"   [OK] Generated: {selector}")
        return True
    else:
        print(f"   [FAIL] Expected: {expected}, Got: {selector}")
        return False


def test_type_only_strategy():
    """Test TYPE_ONLY strategy"""
    print("\n5. Testing TYPE_ONLY strategy...")

    engine = LocationStrategyEngine()
    element = Element(
        index=0,
        uuid='test-uuid',
        tag='input',
        type='email'
    )

    selector = engine._generate_type_only_selector(element)
    expected = 'input[type="email"]'

    if selector == expected:
        print(f"   [OK] Generated: {selector}")
        return True
    else:
        print(f"   [FAIL] Expected: {expected}, Got: {selector}")
        return False


def test_strategy_listing():
    """Test that all 5 new strategies are in the strategy list"""
    print("\n6. Testing strategy listing...")

    engine = LocationStrategyEngine()

    strategy_names = [s['name'] for s in engine.css_strategies]

    expected_strategies = [
        'ARIA_LABEL',
        'TITLE_ATTR',
        'CLASS_UNIQUE',
        'NTH_OF_TYPE',
        'TYPE_ONLY'
    ]

    all_found = True
    for name in expected_strategies:
        if name in strategy_names:
            print(f"   [OK] {name} found in strategy list")
        else:
            print(f"   [FAIL] {name} NOT found in strategy list")
            all_found = False

    return all_found


def verify_phase2_strategies():
    """Run all Phase 2 strategy tests"""
    print("=" * 60)
    print("Phase 2 CSS Strategy Tests")
    print("=" * 60)

    all_passed = True

    tests = [
        test_aria_label_strategy,
        test_title_attr_strategy,
        test_class_unique_strategy,
        test_nth_of_type_strategy,
        test_type_only_strategy,
        test_strategy_listing,
    ]

    for test in tests:
        try:
            result = test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"   [FAIL] Test {test.__name__} raised exception: {e}")
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] ALL PHASE 2 STRATEGY TESTS PASSED")
        print("=" * 60)
        print("\nImplemented Strategies:")
        print("  [OK] ARIA_LABEL - [aria-label=\"value\"]")
        print("  [OK] TITLE_ATTR - [title=\"value\"]")
        print("  [OK] CLASS_UNIQUE - .single-class")
        print("  [OK] NTH_OF_TYPE - tag:nth-of-type(n)")
        print("  [OK] TYPE_ONLY - tag[type=\"value\"]")
        return 0
    else:
        print("[FAIL] SOME PHASE 2 TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(verify_phase2_strategies())
