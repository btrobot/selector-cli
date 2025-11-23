"""
Unit tests for cost calculation module
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.core.locator.cost import (
    StrategyCost,
    STRATEGY_COSTS,
    calculate_length_penalty,
    calculate_special_char_penalty,
    calculate_index_penalty,
    calculate_total_cost,
    CostCalculator,
)


class TestStrategyCost:
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
