#!/usr/bin/env python
"""
Integration test for strategy engine
Verifies that all components work together correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.strategy import LocationStrategyEngine, LocatorType
from src.core.locator.cost import STRATEGY_COSTS
from src.core.element import Element


def test_strategy_engine_initialization():
    """Test that strategy engine initializes correctly with all components"""
    print("\n1. Testing strategy engine initialization...")

    engine = LocationStrategyEngine()

    # Verify components are initialized
    assert engine.validator is not None, "Validator should be initialized"
    assert engine.cost_calculator is not None, "Cost calculator should be initialized"
    assert len(engine.css_strategies) > 0, "CSS strategies should be loaded"
    assert len(engine.xpath_strategies) > 0, "XPath strategies should be loaded"

    print("   [OK] Strategy engine initialized with all components")


def test_strategy_priorities():
    """Test that strategies are properly prioritized"""
    print("\n2. Testing strategy priorities...")

    engine = LocationStrategyEngine()

    # Check CSS strategies are sorted by priority
    for i in range(len(engine.css_strategies) - 1):
        current = engine.css_strategies[i]['priority'].value
        next_priority = engine.css_strategies[i + 1]['priority'].value
        assert current <= next_priority, "CSS strategies should be sorted by priority"

    # Check XPath strategies are sorted by priority
    for i in range(len(engine.xpath_strategies) - 1):
        current = engine.xpath_strategies[i]['priority'].value
        next_priority = engine.xpath_strategies[i + 1]['priority'].value
        assert current <= next_priority, "XPath strategies should be sorted by priority"

    print("   [OK] Strategies are properly prioritized")


def test_locator_type_enum():
    """Test LocatorType enum"""
    print("\n3. Testing LocatorType enum...")

    assert LocatorType.CSS.value == "css"
    assert LocatorType.XPATH.value == "xpath"

    print("   [OK] LocatorType enum correct")


def test_strategy_coverage():
    """Test that core Phase 1 strategies are implemented"""
    print("\n4. Testing Phase 1 strategy coverage...")

    engine = LocationStrategyEngine()

    # Get all strategy names from CSS and XPath strategies
    defined_strategies = set()
    for strategy in engine.css_strategies:
        defined_strategies.add(strategy['name'])
    for strategy in engine.xpath_strategies:
        defined_strategies.add(strategy['name'])

    # Phase 1: Core strategies that should be implemented
    phase1_strategies = {
        'ID_SELECTOR', 'DATA_TESTID', 'LABEL_FOR', 'TYPE_NAME_PLACEHOLDER',
        'HREF', 'TYPE_NAME', 'TYPE_PLACEHOLDER', 'TEXT_CONTENT',
        'XPATH_ID', 'XPATH_ATTR', 'XPATH_TEXT', 'XPATH_POSITION'
    }

    # Check that all Phase 1 strategies are defined
    missing = []
    for strategy_name in phase1_strategies:
        if strategy_name not in defined_strategies:
            missing.append(strategy_name)

    if missing:
        print(f"   [FAIL] Missing Phase 1 strategy definitions: {missing}")
        return False
    else:
        print(f"   [OK] All {len(phase1_strategies)} Phase 1 strategies implemented")

        # Note: Additional strategies will be implemented in Phase 2
        all_strategies = set(STRATEGY_COSTS.keys())
        phase2_strategies = all_strategies - phase1_strategies
        print(f"   [INFO] {len(phase2_strategies)} Phase 2 strategies pending implementation")

        return True


def verify_integration():
    """Run all integration tests"""
    print("="*60)
    print("Strategy Engine Integration Test")
    print("="*60)

    all_passed = True

    try:
        test_strategy_engine_initialization()
    except Exception as e:
        print(f"   [FAIL] Initialization test failed: {e}")
        all_passed = False

    try:
        test_strategy_priorities()
    except Exception as e:
        print(f"   [FAIL] Priority test failed: {e}")
        all_passed = False

    try:
        test_locator_type_enum()
    except Exception as e:
        print(f"   [FAIL] LocatorType test failed: {e}")
        all_passed = False

    try:
        if not test_strategy_coverage():
            all_passed = False
    except Exception as e:
        print(f"   [FAIL] Coverage test failed: {e}")
        all_passed = False

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("[PASS] ALL INTEGRATION TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("[FAIL] SOME INTEGRATION TESTS FAILED")
        print("="*60)
        return 1


if __name__ == '__main__':
    sys.exit(verify_integration())
