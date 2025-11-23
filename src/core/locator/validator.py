"""
Uniqueness validation module for element locators

Provides multiple levels of validation to ensure a locator uniquely
identifies the target element without intersecting with other elements.
"""

from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from src.core.element import Element


class UniquenessValidator:
    """Validates that locators uniquely identify elements"""

    def __init__(self):
        self.validation_cache = {}

    async def is_unique(self, selector: str, page, is_xpath: bool = False) -> bool:
        """
        Level 1: Basic uniqueness check

        Verify that selector matches exactly one element on the page

        Args:
            selector: CSS or XPath selector string
            page: Playwright page object
            is_xpath: True if selector is XPath, False if CSS

        Returns:
            True if selector matches exactly one element, False otherwise
        """
        cache_key = f"{page.url}:{selector}:{is_xpath}"

        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        try:
            if is_xpath:
                locator = page.locator(f"xpath={selector}")
            else:
                locator = page.locator(selector)

            count = await locator.count()
            result = count == 1

            # Cache result
            self.validation_cache[cache_key] = result
            return result

        except Exception:
            # If validation fails, assume not unique
            self.validation_cache[cache_key] = False
            return False

    async def matches_target(self, selector: str, target_element: 'Element', page,
                             is_xpath: bool = False) -> bool:
        """
        Level 2: Target matching check

        Verify that the element matched by selector is the target element

        Args:
            selector: CSS or XPath selector string
            target_element: The element we want to match
            page: Playwright page object
            is_xpath: True if selector is XPath, False if CSS

        Returns:
            True if selector matches the target element
        """
        try:
            if is_xpath:
                matched_locator = page.locator(f"xpath={selector}").first
            else:
                matched_locator = page.locator(selector).first

            # Check if we found anything
            if await matched_locator.count() == 0:
                return False

            # Get critical attributes of matched element
            matched_tag = await matched_locator.evaluate("el => el.tagName.toLowerCase()")

            # Compare with target element
            if matched_tag != target_element.tag:
                return False

            # Check type attribute if present
            if target_element.type:
                matched_type = await matched_locator.get_attribute('type')
                if matched_type != target_element.type:
                    return False

            # Check name attribute if present
            if target_element.name:
                matched_name = await matched_locator.get_attribute('name')
                if matched_name != target_element.name:
                    return False

            # Check id attribute if present
            if target_element.id:
                matched_id = await matched_locator.get_attribute('id')
                if matched_id != target_element.id:
                    return False

            # If all checks pass, likely the right element
            return True

        except Exception:
            # If anything fails, assume not matching
            return False

    async def is_strictly_unique(self, selector: str, target_element: 'Element', page,
                                is_xpath: bool = False) -> bool:
        """
        Level 3: Strict uniqueness check

        Verify that:
        1. Selector matches exactly one element (Level 1)
        2. The matched element is the target (Level 2)

        Args:
            selector: CSS or XPath selector string
            target_element: The element we want to match
            page: Playwright page object
            is_xpath: True if selector is XPath, False if CSS

        Returns:
            True if selector strictly uniquely identifies target element
        """
        # Level 1: Check uniqueness
        if not await self.is_unique(selector, page, is_xpath):
            return False

        # Level 2: Check it matches target
        if not await self.matches_target(selector, target_element, page, is_xpath):
            return False

        # All checks passed
        return True

    async def validate_selector_quality(self, selector: str, target_element: 'Element', page,
                                       is_xpath: bool = False) -> Dict[str, any]:
        """
        Comprehensive selector validation with detailed feedback

        Args:
            selector: CSS or XPath selector string
            target_element: The element we want to match
            page: Playwright page object
            is_xpath: True if selector is XPath, False if CSS

        Returns:
            Dictionary with validation results and feedback
        """
        result = {
            'selector': selector,
            'is_xpath': is_xpath,
            'is_valid': False,
            'level1_unique': False,
            'level2_matches_target': False,
            'quality_score': 0.0,
            'issues': [],
            'recommendations': []
        }

        # Level 1: Check uniqueness
        is_unique = await self.is_unique(selector, page, is_xpath)
        result['level1_unique'] = is_unique

        if not is_unique:
            # Try to get count
            try:
                if is_xpath:
                    count = await page.locator(f"xpath={selector}").count()
                else:
                    count = await page.locator(selector).count()

                result['issues'].append(f'Selector matches {count} elements (expected 1)')
                result['recommendations'].append('Use more specific attributes to target single element')
            except Exception as e:
                result['issues'].append(f'Failed to count matches: {str(e)}')

        # Level 2: Check target match
        matches_target = await self.matches_target(selector, target_element, page, is_xpath)
        result['level2_matches_target'] = matches_target

        if not matches_target:
            result['issues'].append('Selector does not match the target element')
            result['recommendations'].append('Verify critical attributes (id, name, type) match')

        # Overall validity
        result['is_valid'] = is_unique and matches_target

        # Quality score (0-1)
        if result['is_valid']:
            result['quality_score'] = 1.0
        elif matches_target and not is_unique:
            result['quality_score'] = 0.5  # Matches target but not unique
        elif is_unique and not matches_target:
            result['quality_score'] = 0.3  # Unique but wrong element
        else:
            result['quality_score'] = 0.0  # Neither unique nor matches

        return result

    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()

    def cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.validation_cache),
            'cache_keys': list(self.validation_cache.keys())[:10]  # First 10 keys
        }
