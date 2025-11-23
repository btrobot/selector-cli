#!/usr/bin/env python
"""
Simple verification script for cost module
Run this to verify the cost module works correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.cost import (
    STRATEGY_COSTS,
    calculate_length_penalty,
    calculate_special_char_penalty,
    calculate_index_penalty,
    calculate_total_cost,
    CostCalculator,
)


def verify():
    """Run verification tests"""
    print("="*60)
    print("Verifying Cost Module")
    print("="*60)

    all_passed = True

    # Test 1: Strategy costs exist
    print("\n1. Checking strategy costs exist...")
    required_strategies = ['ID_SELECTOR', 'TYPE_NAME', 'XPATH_POSITION']
    for strategy in required_strategies:
        if strategy in STRATEGY_COSTS:
            cost = STRATEGY_COSTS[strategy].total_base_cost
            print(f"   [OK] {strategy}: {cost:.3f}")
        else:
            print(f"   [FAIL] {strategy} NOT FOUND")
            all_passed = False

    # Test 2: Cost ordering (ID should be cheapest)
    print("\n2. Checking cost ordering...")
    id_cost = STRATEGY_COSTS['ID_SELECTOR'].total_base_cost
    xpath_cost = STRATEGY_COSTS['XPATH_POSITION'].total_base_cost

    if id_cost < xpath_cost:
        print(f"   [OK] ID selector ({id_cost:.3f}) cheaper than XPath position ({xpath_cost:.3f})")
    else:
        print(f"   [FAIL] Cost ordering wrong!")
        all_passed = False

    # Test 3: Length penalty
    print("\n3. Checking length penalties...")
    short = "#btn"
    short_penalty = calculate_length_penalty(short)
    print(f"   Short selector '{short}': penalty = {short_penalty} (expected: 0)")

    if short_penalty == 0:
        print("   [OK] Short selector has no penalty")
    else:
        print("   [FAIL] Short selector should have no penalty")
        all_passed = False

    long = 'input[type="email"][name="user-email"][placeholder="Enter email"]'
    long_penalty = calculate_length_penalty(long)
    print(f"   Long selector: penalty = {long_penalty}")

    if long_penalty > 0:
        print("   [OK] Long selector has penalty")
    else:
        print("   [FAIL] Long selector should have penalty")
        all_passed = False

    # Test 4: Special char penalty
    print("\n4. Checking special character penalties...")
    simple = "#submit-btn"
    simple_penalty = calculate_special_char_penalty(simple)
    print(f"   Simple selector '{simple}': penalty = {simple_penalty}")

    complex_sel = '[data-testid="submit-button"]'
    complex_penalty = calculate_special_char_penalty(complex_sel)
    print(f"   Complex selector '{complex_sel}': penalty = {complex_penalty}")

    if complex_penalty > simple_penalty:
        print("   [OK] Complex selector has higher penalty")
    else:
        print("   [FAIL] Complex selector should have higher penalty")
        all_passed = False

    # Test 5: Index penalty
    print("\n5. Checking index penalties...")
    no_index = "button"
    no_index_penalty = calculate_index_penalty(no_index)
    print(f"   Selector without index '{no_index}': penalty = {no_index_penalty}")

    with_index = "button:nth-of-type(2)"
    with_index_penalty = calculate_index_penalty(with_index)
    print(f"   Selector with index '{with_index}': penalty = {with_index_penalty}")

    if with_index_penalty > no_index_penalty:
        print("   [OK] Indexed selector has penalty")
    else:
        print("   [FAIL] Indexed selector should have penalty")
        all_passed = False

    # Test 6: Total cost calculation
    print("\n6. Checking total cost calculation...")
    strategy_cost = STRATEGY_COSTS['ID_SELECTOR']
    selector = "#submit-btn"
    total_cost = calculate_total_cost(strategy_cost, selector)
    print(f"   ID selector '{selector}': total cost = {total_cost:.3f}")

    if total_cost < 0.10:
        print("   [OK] ID selector has low total cost")
    else:
        print("   [FAIL] ID selector should have low cost")
        all_passed = False

    # Test 7: CostCalculator class
    print("\n7. Checking CostCalculator class...")
    calculator = CostCalculator()

    try:
        cost = calculator.calculate('ID_SELECTOR', '#test')
        print(f"   Calculator.calculate('ID_SELECTOR', '#test'): {cost:.3f}")
        print("   [OK] Calculator works")
    except Exception as e:
        print(f"   [FAIL] Calculator failed: {e}")
        all_passed = False

    # Test 8: Cost breakdown
    print("\n8. Checking cost breakdown...")
    breakdown = calculator.get_cost_breakdown('TYPE_NAME', 'input[type="email"][name="user-email"]')

    expected_keys = ['base_cost', 'length_penalty', 'special_char_penalty', 'index_penalty', 'total_cost']
    for key in expected_keys:
        if key in breakdown:
            print(f"   [OK] {key}: {breakdown[key]:.3f}")
        else:
            print(f"   [FAIL] Missing {key}")
            all_passed = False

    # Verify total equals sum
    total = breakdown['total_cost']
    summed = sum([breakdown['base_cost'], breakdown['length_penalty'],
                  breakdown['special_char_penalty'], breakdown['index_penalty']])

    if abs(total - summed) < 0.001:
        print(f"   [OK] Total ({total:.3f}) equals sum of components ({summed:.3f})")
    else:
        print(f"   [FAIL] Total ({total:.3f}) doesn't equal sum ({summed:.3f})")
        all_passed = False

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("[PASS] ALL VERIFICATIONS PASSED")
        print("="*60)
        return 0
    else:
        print("[FAIL] SOME VERIFICATIONS FAILED")
        print("="*60)
        return 1


if __name__ == '__main__':
    sys.exit(verify())
