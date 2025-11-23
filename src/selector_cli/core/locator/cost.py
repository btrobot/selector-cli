"""
Cost calculation module for element location strategies

Implements four-dimensional cost model:
1. Stability (40%): Resistance to page changes
2. Readability (30%): Human comprehension
3. Speed (20%): Selector evaluation speed
4. Maintenance (10%): Long-term maintainability
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class StrategyCost:
    """
    Base cost for a strategy

    Attributes:
        stability: Resistance to page changes (0-1)
        readability: Human comprehension (0-1)
        speed: Selector evaluation speed (0-1)
        maintenance: Long-term maintainability (0-1)
    """

    stability: float
    readability: float
    speed: float
    maintenance: float

    @property
    def total_base_cost(self) -> float:
        """Calculate total base cost (lower is better)"""
        weights = [0.4, 0.3, 0.2, 0.1]
        scores = [self.stability, self.readability, self.speed, self.maintenance]

        # Convert to cost (higher score = lower cost)
        costs = [(1 - score) * weight for score, weight in zip(scores, weights)]
        return sum(costs)


# Strategy cost definitions (P0: optimal strategies)
STRATEGY_COSTS: Dict[str, StrategyCost] = {
    # P0: Optimal strategies (Cost < 0.15)
    'ID_SELECTOR': StrategyCost(
        stability=0.95,    # Very stable - ID rarely changes
        readability=0.95,  # Very readable - simple #id
        speed=0.98,        # Very fast - ID lookup is optimized
        maintenance=0.95,  # Easy to maintain
    ),
    'DATA_TESTID': StrategyCost(
        stability=0.90,    # Stable - test attributes designed for this
        readability=0.85,  # Good - [data-testid="value"] is clear
        speed=0.95,        # Fast - attribute lookup
        maintenance=0.90,  # Easy to maintain
    ),
    'LABEL_FOR': StrategyCost(
        stability=0.85,    # Stable - label association is semantic
        readability=0.85,  # Good - clear relationship
        speed=0.90,        # Fast - combination selector
        maintenance=0.85,  # Maintainable
    ),
    'TYPE_NAME_PLACEHOLDER': StrategyCost(
        stability=0.85,    # Stable - multiple attributes
        readability=0.85,  # Good - very specific
        speed=0.93,        # Fast - attribute matching
        maintenance=0.85,  # Maintainable
    ),
    'HREF': StrategyCost(
        stability=0.85,    # Stable - URLs rarely change
        readability=0.90,  # Very good - semantically clear
        speed=0.98,        # Very fast - href lookup
        maintenance=0.85,  # Maintainable
    ),

    # P1: Excellent strategies (Cost 0.15-0.25)
    'TYPE_NAME': StrategyCost(
        stability=0.80,    # Good - two attributes
        readability=0.80,  # Good - type and name
        speed=0.95,        # Fast - two attributes
        maintenance=0.80,  # Good
    ),
    'TYPE_PLACEHOLDER': StrategyCost(
        stability=0.75,    # Good - but placeholder may change
        readability=0.80,  # Good - clear intent
        speed=0.93,        # Fast
        maintenance=0.80,  # Good
    ),
    'ARIA_LABEL': StrategyCost(
        stability=0.80,    # Good - ARIA attributes stable
        readability=0.80,  # Good - semantic
        speed=0.93,        # Fast
        maintenance=0.80,  # Good
    ),
    'XPATH_ID': StrategyCost(
        stability=0.85,    # Good - ID is stable
        readability=0.60,  # Fair - XPath less readable than CSS
        speed=0.85,        # Slower - XPath evaluation
        maintenance=0.80,  # Good
    ),

    # P2: Good strategies (Cost 0.25-0.40)
    'TITLE_ATTR': StrategyCost(
        stability=0.70,    # Fair - title may change
        readability=0.80,  # Good - hover text
        speed=0.95,        # Fast
        maintenance=0.75,  # Fair
    ),
    'CLASS_UNIQUE': StrategyCost(
        stability=0.65,    # Fair - classes may change
        readability=0.70,  # Fair - .class-name
        speed=0.93,        # Fast - class lookup
        maintenance=0.70,  # Fair - may need updating
    ),
    'NTH_OF_TYPE': StrategyCost(
        stability=0.70,    # Fair - position may change if DOM changes
        readability=0.65,  # Fair - position not semantic
        speed=0.90,        # Fair - nth calculation
        maintenance=0.75,  # Fair - position changes
    ),
    'XPATH_ATTR': StrategyCost(
        stability=0.75,    # Good - attributes stable
        readability=0.50,  # Poor - XPath less readable
        speed=0.85,        # Slower - XPath
        maintenance=0.80,  # Good
    ),

    # P3: Fallback strategies (Cost > 0.40)
    'TEXT_CONTENT': StrategyCost(
        stability=0.60,    # Poor - text may change
        readability=0.80,  # Good - text is readable
        speed=0.95,        # Fast - text search
        maintenance=0.65,  # Fair - text changes
    ),
    'XPATH_TEXT': StrategyCost(
        stability=0.65,    # Fair - text may change
        readability=0.55,  # Poor - XPath text search
        speed=0.85,        # Slower - XPath
        maintenance=0.70,  # Fair
    ),
    'TYPE_ONLY': StrategyCost(
        stability=0.50,    # Poor - type alone not unique
        readability=0.70,  # Fair - type is semantic
        speed=0.98,        # Very fast
        maintenance=0.60,  # Poor - often not unique
    ),
    'XPATH_POSITION': StrategyCost(
        stability=0.50,    # Very poor - position changes often
        readability=0.30,  # Very poor - not human friendly
        speed=0.80,        # Slower - position calculation
        maintenance=0.40,  # Very poor - breaks frequently
    ),
}


def calculate_length_penalty(selector: str) -> float:
    """
    Calculate penalty based on selector length

    Longer selectors are harder to maintain and read

    Args:
        selector: The selector string

    Returns:
        Penalty value (0 or higher)
    """
    length = len(selector)

    if length <= 50:
        return 0.0  # No penalty for short selectors
    elif length <= 100:
        return 0.05  # Small penalty for medium selectors
    elif length <= 150:
        return 0.10  # Medium penalty
    elif length <= 200:
        return 0.15  # Large penalty
    else:
        return 0.20  # Very large penalty for very long selectors


def calculate_special_char_penalty(selector: str) -> float:
    """
    Calculate penalty for special characters

    Special characters reduce readability

    Args:
        selector: The selector string

    Returns:
        Penalty value (0 or higher)
    """
    # Characters that reduce readability
    css_special_chars = ['$', '[', ']', '(', ')', '=']
    xpath_special_chars = ['/', '@', '[', ']', '(', ')', '=', '"', "'"]

    # Count special characters
    if selector.startswith('//'):
        # XPath - use XPath special chars
        special_count = sum(selector.count(ch) for ch in xpath_special_chars)
    else:
        # CSS - use CSS special chars
        special_count = sum(selector.count(ch) for ch in css_special_chars)

    return special_count * 0.05  # Each special char adds 0.05 penalty


def calculate_index_penalty(selector: str) -> float:
    """
    Calculate penalty for index-based selectors

    Index-based selectors are fragile to DOM changes

    Args:
        selector: The selector string

    Returns:
        Penalty value (0 or higher)
    """
    has_index = any(x in selector for x in [
        ':nth-of-type',
        ':nth-child',
        '[1]', '[2]', '[3]',  # Position indices
        'position()',
    ])

    return 0.10 if has_index else 0.0


def calculate_total_cost(strategy_cost: StrategyCost, selector: str) -> float:
    """
    Calculate total cost for a selector

    Args:
        strategy_cost: Base cost from strategy
        selector: The generated selector string

    Returns:
        Total cost (base cost + penalties)
    """
    # Start with base cost from strategy
    total_cost = strategy_cost.total_base_cost

    # Add dynamic penalties
    total_cost += calculate_length_penalty(selector)
    total_cost += calculate_special_char_penalty(selector)
    total_cost += calculate_index_penalty(selector)

    return round(total_cost, 3)  # Round to 3 decimal places


# CostCalculator class wrapping the calculations
class CostCalculator:
    """Calculator for selector costs"""

    def calculate(self, strategy_name: str, selector: str) -> float:
        """
        Calculate total cost for a selector

        Args:
            strategy_name: Name of the strategy used
            selector: The generated selector string

        Returns:
            Total cost value
        """
        if strategy_name not in STRATEGY_COSTS:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy_cost = STRATEGY_COSTS[strategy_name]
        return calculate_total_cost(strategy_cost, selector)

    def get_base_cost(self, strategy_name: str) -> float:
        """Get base cost for a strategy (without penalties)"""
        if strategy_name not in STRATEGY_COSTS:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return STRATEGY_COSTS[strategy_name].total_base_cost

    def get_cost_breakdown(self, strategy_name: str, selector: str) -> Dict[str, float]:
        """
        Get detailed cost breakdown

        Args:
            strategy_name: Name of the strategy
            selector: The selector string

        Returns:
            Dictionary with cost components
        """
        if strategy_name not in STRATEGY_COSTS:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy_cost = STRATEGY_COSTS[strategy_name]

        return {
            'base_cost': strategy_cost.total_base_cost,
            'length_penalty': calculate_length_penalty(selector),
            'special_char_penalty': calculate_special_char_penalty(selector),
            'index_penalty': calculate_index_penalty(selector),
            'total_cost': calculate_total_cost(strategy_cost, selector),
        }
