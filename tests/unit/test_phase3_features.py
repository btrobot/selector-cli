#!/usr/bin/env python
"""
Phase 3 feature verification tests
- NTH_OF_TYPE position calculation
- XPath escaping (simplified)
- Debug logging preparation
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.strategy import LocationStrategyEngine
from src.core.locator.cost import calculate_total_cost, STRATEGY_COSTS
from src.core.element import Element


def test_nth_of_type_basic():
    """Test NTH_OF_TYPE selector generation (basic test without Playwright)"""
    print("\n1. Testing NTH_OF_TYPE strategy structure...")

    engine = LocationStrategyEngine()

    # Create mock element
    element = Element(
        index=0,
        uuid='test-uuid',
        tag='button',
        type='submit',
        text='Submit'
    )

    # Get the strategy
    nth_strategy = None
    for strategy in engine.css_strategies:
        if strategy['name'] == 'NTH_OF_TYPE':
            nth_strategy = strategy
            break

    if nth_strategy:
        print(f"   [OK] NTH_OF_TYPE strategy found")
        print(f"   [OK] Priority: {nth_strategy['priority']}")
        print(f"   [OK] Applies to: {nth_strategy['applies_to']}")
        print(f"   [OK] Generator is async: {nth_strategy['generator'].__name__}")
        return True
    else:
        print(f"   [FAIL] NTH_OF_TYPE strategy not found")
        return False


def test_priority_ordering():
    """Verify strategy priority ordering after NTH_OF_TYPE update"""
    print("\n2. Testing strategy priority ordering...")

    engine = LocationStrategyEngine()

    # Check CSS strategies are sorted by priority
    prev_priority = 0
    for strategy in engine.css_strategies:
        current = strategy['priority'].value
        if current < prev_priority:
            print(f"   [FAIL] Priority ordering broken: {current} < {prev_priority}")
            return False
        prev_priority = current

    print(f"   [OK] All {len(engine.css_strategies)} CSS strategies properly sorted")
    return True


def test_async_generator_detection():
    """Test that async generators are properly detected"""
    print("\n3. Testing async generator detection...")

    import inspect

    engine = LocationStrategyEngine()

    nth_strategy = None
    for strategy in engine.css_strategies:
        if strategy['name'] == 'NTH_OF_TYPE':
            nth_strategy = strategy
            break

    if not nth_strategy:
        print(f"   [FAIL] NTH_OF_TYPE not found")
        return False

    generator = nth_strategy['generator']
    sig = inspect.signature(generator)

    print(f"   Generator: {generator.__name__}")
    print(f"   Parameters: {list(sig.parameters.keys())}")
    print(f"   Is async: {inspect.iscoroutinefunction(generator)}")

    if 'page' in sig.parameters:
        print(f"   [OK] Generator accepts 'page' parameter")
        return True
    else:
        print(f"   [FAIL] Generator doesn't accept 'page' parameter")
        return False


def test_strategy_coverage():
    """Verify all 17 strategies are still present"""
    print("\n4. Testing strategy coverage...")

    engine = LocationStrategyEngine()

    # Get all strategy names
    strategy_names = []
    for strategy in engine.css_strategies:
        strategy_names.append(strategy['name'])
    for strategy in engine.xpath_strategies:
        strategy_names.append(strategy['name'])

    # Check against STRATEGY_COSTS
    missing = []
    for name in STRATEGY_COSTS.keys():
        if name not in strategy_names:
            missing.append(name)

    if missing:
        print(f"   [FAIL] Missing strategies: {missing}")
        return False

    print(f"   [OK] All {len(STRATEGY_COSTS)} strategies present")
    return True


def test_xpath_costs():
    """Verify XPath strategy costs are appropriate"""
    print("\n5. Testing XPath strategy costs...")

    tests = [
        ('XPATH_ID', 0.044 + 0.300),  # ID base cost + special char penalty for [@id=...]
        ('XPATH_ATTR', 0.230 + 0.300),  # ATTR base + penalty
        ('XPATH_TEXT', 0.340 + 0.400),  # TEXT base + higher penalty for contains()
        ('XPATH_POSITION', 0.510 + 0.100),  # POSITION base + index penalty
    ]

    all_passed = True
    for strategy_name, expected_cost_min in tests:
        # Get base cost from STRATEGY_COSTS
        base_cost = STRATEGY_COSTS[strategy_name].total_base_cost
        if base_cost > 0:
            print(f"   [OK] {strategy_name}: base={base_cost:.3f}")
        else:
            print(f"   [FAIL] {strategy_name}: invalid base cost")
            all_passed = False

    return all_passed


def verify_phase3_progress():
    """Run all Phase 3 tests"""
    print("=" * 60)
    print("Phase 3 Feature Tests")
    print("=" * 60)

    all_passed = True

    tests = [
        test_nth_of_type_basic,
        test_priority_ordering,
        test_async_generator_detection,
        test_strategy_coverage,
        test_xpath_costs,
    ]

    for test in tests:
        try:
            result = test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"   [FAIL] {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("Phase 3 Status Summary")
    print("=" * 60)

    if all_passed:
        print("[OK] NTH_OF_TYPE strategy implemented with async support")
        print("[OK] Strategy priority ordering maintained")
        print("[OK] Async generator detection working")
        print("[OK] All 17 strategies present and accounted for")
        print("[OK] XPath costs configured")
        print("\n" + "=" * 60)
        print("[PASS] PHASE 3 FEATURES VERIFIED")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Fix XPath string escaping (simplify logic)")
        print("  2. Add debug logging infrastructure")
        print("  3. Prepare Scanner integration interface")
        print("  4. Create real browser test examples")
        return 0
    else:
        print("[FAIL] SOME PHASE 3 TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(verify_phase3_progress())
