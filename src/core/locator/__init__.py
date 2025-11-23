"""
Element location strategy module

Provides intelligent element locator generation with uniqueness verification
and cost-based strategy selection.
"""

from .strategy import LocationStrategyEngine, LocationResult
from .cost import calculate_total_cost, StrategyCost, STRATEGY_COSTS
from .validator import UniquenessValidator

__all__ = [
    'LocationStrategyEngine',
    'LocationResult',
    'calculate_total_cost',
    'StrategyCost',
    'STRATEGY_COSTS',
    'UniquenessValidator',
]
