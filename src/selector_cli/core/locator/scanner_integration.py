"""
Scanner/Collection Integration Interface
Connects the LocationStrategyEngine with the element scanner system
"""

from typing import List, Optional, Dict, Any
from ..element import Element
from ...strategy import LocationStrategyEngine, LocationResult
from .logging import logger
from playwright.async_api import Page


class LocatorIntegrationEngine:
    """
    Integration engine that connects the scanner/collection system
    with the LocationStrategyEngine for automatic locator generation
    """

    def __init__(self):
        self.strategy_engine = LocationStrategyEngine()
        self.stats = {
            'total_elements': 0,
            'successful': 0,
            'failed': 0,
            'by_strategy': {},
            'by_cost': {
                'low': 0,  # cost < 0.15 (P0)
                'medium': 0,  # cost 0.15-0.40 (P1-P2)
                'high': 0,  # cost > 0.40 (P3)
            }
        }

    async def process_collection(self, elements: List[Element], page: Page) -> Dict[str, Any]:
        """
        Process a collection of elements and generate locators for each

        Args:
            elements: List of elements from scanner
            page: Playwright page object

        Returns:
            Dictionary with results and statistics
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing collection of {len(elements)} elements")
        logger.info(f"{'='*60}")

        self.stats = {
            'total_elements': len(elements),
            'successful': 0,
            'failed': 0,
            'by_strategy': {},
            'by_cost': {
                'low': 0,
                'medium': 0,
                'high': 0,
            }
        }

        results = []

        for idx, element in enumerate(elements):
            logger.info(f"\n[Element {idx+1}/{len(elements)}] Processing: {element}")

            # Find best locator
            result = await self.strategy_engine.find_best_locator(element, page)

            if result and result.is_unique:
                # Success
                results.append({
                    'element': element,
                    'locator': result,
                    'success': True,
                })
                self.stats['successful'] += 1

                # Update strategy stats
                strategy = result.strategy
                self.stats['by_strategy'][strategy] = self.stats['by_strategy'].get(strategy, 0) + 1

                # Update cost stats
                if result.cost < 0.15:
                    self.stats['by_cost']['low'] += 1
                elif result.cost < 0.40:
                    self.stats['by_cost']['medium'] += 1
                else:
                    self.stats['by_cost']['high'] += 1

                logger.info(f"  ✓ SUCCESS: {result.strategy} (cost: {result.cost:.3f})")
                logger.info(f"    Selector: {result.selector}")
            else:
                # Failure
                results.append({
                    'element': element,
                    'locator': None,
                    'success': False,
                })
                self.stats['failed'] += 1
                logger.warning(f"  ✗ FAILED: Could not find unique locator")

        # Print summary
        self._print_summary()

        return {
            'results': results,
            'stats': self.stats
        }

    def _print_summary(self):
        """Print processing summary statistics"""
        logger.info(f"\n{'='*60}")
        logger.info("Processing Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Total elements: {self.stats['total_elements']}")
        logger.info(f"Successful: {self.stats['successful']} ({self.stats['successful']/self.stats['total_elements']*100:.1f}%)")
        logger.info(f"Failed: {self.stats['failed']} ({self.stats['failed']/self.stats['total_elements']*100:.1f}%)")

        # Strategy breakdown
        if self.stats['by_strategy']:
            logger.info("\nStrategy Usage:")
            for strategy, count in sorted(self.stats['by_strategy'].items(),
                                        key=lambda x: x[1], reverse=True):
                logger.info(f"  {strategy:25s}: {count:3d} elements")

        # Cost breakdown
        logger.info("\nCost Distribution:")
        logger.info(f"  Low cost (< 0.15):     {self.stats['by_cost']['low']:3d} ({self.stats['by_cost']['low']/self.stats['total_elements']*100:.1f}%)")
        logger.info(f"  Medium cost (0.15-0.40): {self.stats['by_cost']['medium']:3d} ({self.stats['by_cost']['medium']/self.stats['total_elements']*100:.1f}%)")
        logger.info(f"  High cost (> 0.40):      {self.stats['by_cost']['high']:3d} ({self.stats['by_cost']['high']/self.stats['total_elements']*100:.1f}%)")

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()

    def enable_debug_logging(self):
        """Enable debug logging for detailed output"""
        from .logging import enable_debug_logging
        enable_debug_logging()

    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'total_elements': 0,
            'successful': 0,
            'failed': 0,
            'by_strategy': {},
            'by_cost': {
                'low': 0,
                'medium': 0,
                'high': 0,
            }
        }