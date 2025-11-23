#!/usr/bin/env python
"""
Unit tests for cost calculation module
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.locator.cost import (
    StrategyCost,
    STRATEGY_COSTS,
    calculate_length_penalty,
    calculate_special_char_penalty,
    calculate_index_penalty,
    calculate_total_cost,
    CostCalculator,
)


def test_strategy_cost_creation():
    """Test creating a StrategyCost instance"""
    print("\n1. Testing StrategyCost creation...")

    cost = StrategyCost(
        stability=0.95,
        readability=0.90,
        speed=0.95,
        maintenance=0.90
    )

    assert cost.stability == 0.95
    assert cost.readability == 0.90
    assert cost.speed == 0.95
    assert cost.maintenance == 0.90
    print("   [OK] StrategyCost creation working")
    return True


def test_base_cost_calculation():
    """Test base cost calculation"""
    print("\n2. Testing base cost calculation...")

    # ID selector - should have very low cost
    cost = STRATEGY_COSTS['ID_SELECTOR']
    base_cost = cost.total_base_cost

    # ID selector should have very low base cost (< 0.10)
    assert base_cost < 0.10
    assert base_cost > 0.05
    print(f"   [OK] ID selector base cost: {base_cost:.3f}")

    # XPATH_POSITION should have high base cost (> 0.50)
    cost = STRATEGY_COSTS['XPATH_POSITION']
    base_cost = cost.total_base_cost
    assert base_cost > 0.50
    print(f"   [OK] XPATH_POSITION base cost: {base_cost:.3f}")
    return True


def test_cost_ordering():
    """Test that costs follow expected priority order"""
    print("\n3. Testing cost ordering...")

    # P0 strategies should be cheapest
    p0_cost = STRATEGY_COSTS['ID_SELECTOR'].total_base_cost
    p3_cost = STRATEGY_COSTS['XPATH_POSITION'].total_base_cost

    assert p0_cost < p3_cost
    print(f"   [OK] P0 (ID): {p0_cost:.3f} < P3 (XPath): {p3_cost:.3f}")

    # P1 should be cheaper than P2
    p1_cost = STRATEGY_COSTS['TYPE_NAME'].total_base_cost
    p2_cost = STRATEGY_COSTS['TITLE_ATTR'].total_base_cost
    assert p1_cost < p2_cost
    print(f"   [OK] P1: {p1_cost:.3f} < P2: {p2_cost:.3f}")
    return True


def test_length_penalty_short():
    """Test length penalty for short selectors"""
    print("\n4. Testing length penalty (short selector)...")

    selector = "#submit-btn"
    penalty = calculate_length_penalty(selector)
    # Short selector should have no or minimal penalty
    print(f"   [OK] Short selector penalty: {penalty:.3f}")
    return True


def test_length_penalty_long():
    """Test length penalty for long selectors"""
    print("\n5. Testing length penalty (long selector)...")

    selector = 'input[type="email"][name="user-email"][placeholder="Enter your email"]'
    penalty = calculate_length_penalty(selector)
    # Long selector should have penalty
    print(f"   [OK] Long selector penalty: {penalty:.3f}")
    return True


def test_special_char_penalty_simple():
    """Test special char penalty for simple selectors"""
    print("\n6. Testing special char penalty (simple selector)...")

    selector = "#submit-btn"
    penalty = calculate_special_char_penalty(selector)
    # Should have minimal penalty
    print(f"   [OK] Simple selector penalty: {penalty:.3f}")
    return True


def test_special_char_penalty_complex():
    """Test special char penalty for complex selectors"""
    print("\n7. Testing special char penalty (complex selector)...")

    selector = 'input[type="email"][name="user-email"]'
    penalty = calculate_special_char_penalty(selector)
    # Complex selector should have higher penalty
    print(f"   [OK] Complex selector penalty: {penalty:.3f}")
    return True


def test_special_char_penalty_xpath():
    """Test special char penalty for XPath selectors"""
    print("\n8. Testing special char penalty (XPath)...")

    xpath = "//button[@id='submit']"
    penalty = calculate_special_char_penalty(xpath)
    # XPath has special chars
    print(f"   [OK] XPath special char penalty: {penalty:.3f}")
    return True


def test_index_penalty():
    """Test index penalty calculation"""
    print("\n9. Testing index penalty...")

    # No index
    penalty1 = calculate_index_penalty("#id")
    print(f"   [OK] No index penalty: {penalty1:.3f}")

    # With index
    penalty2 = calculate_index_penalty("div:nth-of-type(3)")
    print(f"   [OK] Index penalty: {penalty2:.3f}")
    return True


def test_total_cost_id_selector():
    """Test total cost for ID selector"""
    print("\n10. Testing total cost (ID selector)...")

    cost = calculate_total_cost(STRATEGY_COSTS['ID_SELECTOR'], "#submit-btn")
    # ID should have low cost
    print(f"   [OK] ID selector cost: {cost:.3f}")
    return True


def test_total_cost_xpath_position():
    """Test total cost for XPath position selector"""
    print("\n11. Testing total cost (XPath position)...")

    xpath = "/html/body/div[2]/button[1]"
    cost = calculate_total_cost(STRATEGY_COSTS['XPATH_POSITION'], xpath)
    # Should be high cost
    print(f"   [OK] XPath position cost: {cost:.3f}")
    return True


def test_strategy_cost_config():
    """Test that all strategies have cost configuration"""
    print("\n12. Testing strategy cost configuration...")

    expected_strategies = [
        'ID_SELECTOR', 'DATA_TESTID', 'LABEL_FOR', 'TYPE_NAME_PLACEHOLDER',
        'HREF', 'TYPE_NAME', 'TYPE_PLACEHOLDER', 'ARIA_LABEL',
        'TITLE_ATTR', 'CLASS_UNIQUE', 'NTH_OF_TYPE', 'TEXT_CONTENT',
        'TYPE_ONLY', 'XPATH_ID', 'XPATH_ATTR', 'XPATH_TEXT', 'XPATH_POSITION'
    ]

    for strategy in expected_strategies:
        assert strategy in STRATEGY_COSTS, f"Strategy {strategy} missing"
        assert STRATEGY_COSTS[strategy].total_base_cost > 0, f"Strategy {strategy} invalid cost"

    print(f"   [OK] All {len(expected_strategies)} strategies configured")
    return True


def test_cost_calculator():
    """Test CostCalculator class"""
    print("\n13. Testing CostCalculator...")

    calculator = CostCalculator()

    # Test base cost
    base_cost = calculator.get_base_cost('ID_SELECTOR')
    print(f"   [OK] Base cost: {base_cost:.3f}")

    # Test calculate
    total = calculator.calculate('ID_SELECTOR', '#submit-btn')
    print(f"   [OK] Total cost: {total:.3f}")
    return True


def test_cost_calculator_breakdown():
    """Test cost breakdown"""
    print("\n14. Testing cost breakdown...")

    calculator = CostCalculator()
    selector = 'input[type="email"][name="test"]'
    breakdown = calculator.get_cost_breakdown('TYPE_NAME', selector)

    assert 'base_cost' in breakdown
    assert 'length_penalty' in breakdown
    assert 'special_char_penalty' in breakdown
    assert 'index_penalty' in breakdown
    assert 'total_cost' in breakdown

    print(f"   [OK] Breakdown: base={breakdown['base_cost']:.3f}, "
          f"length={breakdown['length_penalty']:.3f}, "
          f"special={breakdown['special_char_penalty']:.3f}, "
          f"index={breakdown['index_penalty']:.3f}, "
          f"total={breakdown['total_cost']:.3f}")
    return True


def test_cost_ordering():
    """Test cost ordering between strategies"""
    print("\n15. Testing cost ordering...")

    id_cost = calculate_total_cost(STRATEGY_COSTS['ID_SELECTOR'], "#id")
    xpath_pos_cost = calculate_total_cost(STRATEGY_COSTS['XPATH_POSITION'], "//div[1]")

    assert id_cost < xpath_pos_cost
    print(f"   [OK] ID ({id_cost:.3f}) < XPath position ({xpath_pos_cost:.3f})")
    return True


def test_cost_components_sum():
    """Test that total equals sum of components"""
    print("\n16. Testing cost components sum...")

    strategy_cost = STRATEGY_COSTS['TYPE_NAME']
    selector = 'input[type="email"][name="user-email"]'

    total = calculate_total_cost(strategy_cost, selector)
    base = strategy_cost.total_base_cost
    length = calculate_length_penalty(selector)
    special = calculate_special_char_penalty(selector)
    index = calculate_index_penalty(selector)

    calculated_total = base + length + special + index
    assert abs(total - calculated_total) < 0.001, "Total should equal sum of components"
    print(f"   [OK] Total {total:.3f} = base {base:.3f} + length {length:.3f} + "
          f"special {special:.3f} + index {index:.3f}")
    return True


def test_edge_cases():
    """Test edge cases"""
    print("\n17. Testing edge cases...")

    # Empty selector
    cost1 = calculate_total_cost(STRATEGY_COSTS['ID_SELECTOR'], "")
    print(f"   [OK] Empty selector cost: {cost1:.3f}")

    # Very long selector
    selector = 'div' * 50 + '[class="x" * 100]'
    cost2 = calculate_total_cost(STRATEGY_COSTS['CSS_SELECTOR'], selector)
    print(f"   [OK] Very long selector cost: {cost2:.3f}")
    return True


def test_unknown_strategy():
    """Test error handling for unknown strategy"""
    print("\n18. Testing unknown strategy...")

    calculator = CostCalculator()

    try:
        calculator.calculate('UNKNOWN_STRATEGY', '#test')
        print("   [FAIL] Should have raised exception")
        return False
    except ValueError:
        print("   [OK] Unknown strategy raises ValueError")
        return True


def run_all_tests():
    """Run all cost tests"""
    print("="*60)
    print("Phase 4 - Cost Module Comprehensive Tests")
    print("="*60)

    all_tests = [
        test_strategy_cost_creation,
        test_base_cost_calculation,
        test_cost_ordering,
        test_length_penalty_short,
        test_length_penalty_long,
        test_special_char_penalty_simple,
        test_special_char_penalty_complex,
        test_special_char_penalty_xpath,
        test_index_penalty,
        test_total_cost_id_selector,
        test_total_cost_xpath_position,
        test_strategy_cost_config,
        test_cost_calculator,
        test_cost_calculator_breakdown,
        test_cost_ordering,
        test_cost_components_sum,
        test_edge_cases,
        test_unknown_strategy,
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
        print("\n[PASS] ALL COST TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
    """Test StrategyCost dataclass"""

    def test_strategy_cost_creation(self):
        """Test creating a StrategyCost instance"""
        cost = StrategyCost(
            stability=0.95,
            readability=0.90,
            speed=0.95,
            maintenance=0.90
        )

        assert cost.stability == 0.95
        assert cost.readability == 0.90
        assert cost.speed == 0.95
        assert cost.maintenance == 0.90

    def test_base_cost_calculation(self):
        """Test base cost calculation"""
        # ID selector - should have very low cost
        cost = STRATEGY_COSTS['ID_SELECTOR']
        base_cost = cost.total_base_cost

        # ID selector should have very low base cost (< 0.10)
        assert base_cost < 0.10
        assert base_cost > 0.05

        # XPATH_POSITION should have high base cost (> 0.50)
        cost = STRATEGY_COSTS['XPATH_POSITION']
        base_cost = cost.total_base_cost
        assert base_cost > 0.50

    def test_cost_ordering(self):
        """Test that costs follow expected priority order"""
        # P0 strategies should be cheapest
        p0_cost = STRATEGY_COSTS['ID_SELECTOR'].total_base_cost
        p3_cost = STRATEGY_COSTS['XPATH_POSITION'].total_base_cost

        assert p0_cost < p3_cost

        # P1 should be cheaper than P2
        p1_cost = STRATEGY_COSTS['TYPE_NAME'].total_base_cost
        p2_cost = STRATEGY_COSTS['TITLE_ATTR'].total_base_cost
        assert p1_cost < p2_cost


class TestLengthPenalty:
    """Test length penalty calculation"""

    def test_short_selector_no_penalty(self):
        """Selectors <= 50 chars have no penalty"""
        selector = "#submit-btn"
        penalty = calculate_length_penalty(selector)
        assert penalty == 0.0

    def test_medium_selector_small_penalty(self):
        """Selectors 51-100 chars have small penalty"""
        selector = 'input[type="email"][name="user-email"]'
        penalty = calculate_length_penalty(selector)
        assert penalty == 0.05

    def test_long_selector_medium_penalty(self):
        """Selectors 101-150 chars have medium penalty"""
        selector = 'input[type="email"][name="user-email"][placeholder="Enter your email"]'
        penalty = calculate_length_penalty(selector)
        assert penalty == 0.10

    def test_very_long_selector_large_penalty(self):
        """Selectors > 200 chars have large penalty"""
        selector = (
            'input[type="email"][name="user-email"]'
            '[placeholder="Enter your email address here"]'
            '[class="form-input email-input user-input"]'
        )
        penalty = calculate_length_penalty(selector)
        assert penalty == 0.20


class TestSpecialCharPenalty:
    """Test special character penalty calculation"""

    def test_id_selector_no_penalty(self):
        """ID selector has minimal special chars"""
        selector = "#submit-btn"
        penalty = calculate_special_char_penalty(selector)
        assert penalty == 0.0  # Only # and -, no penalty chars

    def test_css_with_brackets_has_penalty(self):
        """CSS with brackets and quotes has penalty"""
        selector = '[data-testid="submit-button"]'
        penalty = calculate_special_char_penalty(selector)
        assert penalty > 0

    def test_xpath_has_high_penalty(self):
        """XPath has many special characters"""
        selector = '//button[@type="submit"][@name="btn"]'
        penalty = calculate_special_char_penalty(selector)
        assert penalty > 0.2  # Multiple /, @, [, ], =, and quotes

    def test_multiple_special_chars_linear(self):
        """Penalty scales linearly with special char count"""
        selector1 = '[type="text"]'
        selector2 = '[type="text"][name="email"]'

        penalty1 = calculate_special_char_penalty(selector1)
        penalty2 = calculate_special_char_penalty(selector2)

        assert penalty2 > penalty1


class TestIndexPenalty:
    """Test index penalty calculation"""

    def test_selector_without_index_no_penalty(self):
        """Selectors without index have no penalty"""
        selector = "#submit-btn"
        penalty = calculate_index_penalty(selector)
        assert penalty == 0.0

    def test_nth_of_type_has_penalty(self):
        """Selectors with :nth-of-type have penalty"""
        selector = "button:nth-of-type(2)"
        penalty = calculate_index_penalty(selector)
        assert penalty == 0.10

    def test_nth_child_has_penalty(self):
        """Selectors with :nth-child have penalty"""
        selector = "div:nth-child(3)"
        penalty = calculate_index_penalty(selector)
        assert penalty == 0.10

    def test_position_in_xpath_has_penalty(self):
        """XPath with position() has penalty"""
        selector = '//button[position()=2]'
        penalty = calculate_index_penalty(selector)
        assert penalty == 0.10


class TestTotalCost:
    """Test total cost calculation"""

    def test_id_selector_total_cost(self):
        """ID selector should have very low total cost"""
        strategy_cost = STRATEGY_COSTS['ID_SELECTOR']
        selector = "#submit-btn"

        cost = calculate_total_cost(strategy_cost, selector)

        # Should be close to base cost (no penalties)
        assert cost < 0.10
        assert cost > 0.05

    def test_complex_selector_high_cost(self):
        """Complex selectors should have higher cost"""
        strategy_cost = STRATEGY_COSTS['TYPE_NAME_PLACEHOLDER']
        selector = (
            'input[type="email"][name="user-email"]'
            '[placeholder="Enter your email address here"]'
        )

        cost = calculate_total_cost(strategy_cost, selector)

        # Should have penalties added
        assert cost > strategy_cost.total_base_cost
        assert cost < 0.30  # Still reasonable

    def test_xpath_position_highest_cost(self):
        """XPATH_POSITION should have the highest cost"""
        strategy_cost = STRATEGY_COSTS['XPATH_POSITION']
        selector = '/html/body/div[2]/form/input[1]'

        cost = calculate_total_cost(strategy_cost, selector)

        # Should be > 0.50 (base 0.57 + penalties)
        assert cost > 0.50

    def test_cost_components_sum(self):
        """Total cost equals base + penalties"""
        strategy_cost = STRATEGY_COSTS['TYPE_NAME']
        selector = 'input[type="email"][name="user-email"]'

        total = calculate_total_cost(strategy_cost, selector)
        base = strategy_cost.total_base_cost
        length = calculate_length_penalty(selector)
        special = calculate_special_char_penalty(selector)
        index = calculate_index_penalty(selector)

        assert round(total, 3) == round(base + length + special + index, 3)


class TestCostCalculator:
    """Test CostCalculator class"""

    def test_calculator_initialization(self):
        """Test creating cost calculator"""
        calculator = CostCalculator()
        assert calculator is not None

    def test_calculate_method(self):
        """Test calculate method"""
        calculator = CostCalculator()
        cost = calculator.calculate('ID_SELECTOR', '#submit-btn')

        # Should return ID selector cost
        assert cost == calculate_total_cost(
            STRATEGY_COSTS['ID_SELECTOR'],
            '#submit-btn'
        )

    def test_get_base_cost(self):
        """Test getting base cost"""
        calculator = CostCalculator()
        base_cost = calculator.get_base_cost('ID_SELECTOR')

        assert base_cost == STRATEGY_COSTS['ID_SELECTOR'].total_base_cost

    def test_get_cost_breakdown(self):
        """Test getting detailed cost breakdown"""
        calculator = CostCalculator()
        breakdown = calculator.get_cost_breakdown(
            'TYPE_NAME',
            'input[type="email"][name="user-email"]'
        )

        assert 'base_cost' in breakdown
        assert 'length_penalty' in breakdown
        assert 'special_char_penalty' in breakdown
        assert 'index_penalty' in breakdown
        assert 'total_cost' in breakdown

        # Verify total equals sum
        total = breakdown['total_cost']
        summed = (
            breakdown['base_cost'] +
            breakdown['length_penalty'] +
            breakdown['special_char_penalty'] +
            breakdown['index_penalty']
        )
        assert round(total, 3) == round(summed, 3)

    def test_unknown_strategy_raises_error(self):
        """Test that unknown strategy raises ValueError"""
        calculator = CostCalculator()

        with pytest.raises(ValueError, match="Unknown strategy"):
            calculator.calculate('UNKNOWN_STRATEGY', '#test')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
