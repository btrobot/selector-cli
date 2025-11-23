"""
Highlighter utility for visual feedback
"""
from typing import List, Optional, Set
from playwright.async_api import Page, Locator
from src.core.element import Element


class Highlighter:
    """Highlight elements in the browser for visual feedback"""

    # Default highlight style
    HIGHLIGHT_STYLE = """
        outline: 3px solid #ff6b6b !important;
        outline-offset: 2px !important;
        background-color: rgba(255, 107, 107, 0.1) !important;
    """

    # Alternative colors for different contexts
    COLORS = {
        'default': '#ff6b6b',  # Red
        'success': '#51cf66',  # Green
        'info': '#339af0',     # Blue
        'warning': '#ffd43b',  # Yellow
    }

    def __init__(self, page: Page):
        self.page = page
        self.highlighted_selectors: Set[str] = set()

    async def highlight_elements(
        self,
        elements: List[Element],
        color: str = 'default'
    ) -> int:
        """
        Highlight elements in the browser

        Args:
            elements: List of elements to highlight
            color: Color theme ('default', 'success', 'info', 'warning')

        Returns:
            Number of elements successfully highlighted
        """
        if not elements:
            return 0

        color_code = self.COLORS.get(color, self.COLORS['default'])
        count = 0

        for elem in elements:
            try:
                # Use CSS selector if available, otherwise XPath
                selector = elem.css_selector or elem.xpath
                if not selector:
                    continue

                # Create locator
                if elem.css_selector:
                    locator = self.page.locator(elem.css_selector)
                else:
                    locator = self.page.locator(f"xpath={elem.xpath}")

                # Check if element exists
                element_count = await locator.count()
                if element_count == 0:
                    continue

                # Highlight the element(s)
                await locator.evaluate(
                    f"""
                    (elements) => {{
                        const elemArray = Array.isArray(elements) ? elements : [elements];
                        elemArray.forEach(el => {{
                            el.style.outline = '3px solid {color_code}';
                            el.style.outlineOffset = '2px';
                            el.style.backgroundColor = '{color_code}20';
                            el.setAttribute('data-selector-highlighted', 'true');
                        }});
                    }}
                    """
                )

                # Track selector
                self.highlighted_selectors.add(selector)
                count += element_count

            except Exception as e:
                # Skip elements that fail to highlight
                continue

        return count

    async def unhighlight_all(self) -> int:
        """
        Remove all highlights from the page

        Returns:
            Number of elements unhighlighted
        """
        if not self.highlighted_selectors:
            return 0

        try:
            # Remove highlights from all marked elements
            count = await self.page.evaluate(
                """
                () => {
                    const highlighted = document.querySelectorAll('[data-selector-highlighted="true"]');
                    highlighted.forEach(el => {
                        el.style.outline = '';
                        el.style.outlineOffset = '';
                        el.style.backgroundColor = '';
                        el.removeAttribute('data-selector-highlighted');
                    });
                    return highlighted.length;
                }
                """
            )

            # Clear tracked selectors
            self.highlighted_selectors.clear()

            return count

        except Exception:
            # Clear tracking even if unhighlight fails
            self.highlighted_selectors.clear()
            return 0

    async def highlight_selector(
        self,
        selector: str,
        color: str = 'default',
        is_xpath: bool = False
    ) -> int:
        """
        Highlight elements by selector

        Args:
            selector: CSS selector or XPath
            color: Color theme
            is_xpath: Whether selector is XPath

        Returns:
            Number of elements highlighted
        """
        try:
            color_code = self.COLORS.get(color, self.COLORS['default'])

            if is_xpath:
                locator = self.page.locator(f"xpath={selector}")
            else:
                locator = self.page.locator(selector)

            count = await locator.count()
            if count == 0:
                return 0

            await locator.evaluate(
                f"""
                (elements) => {{
                    const elemArray = Array.isArray(elements) ? elements : [elements];
                    elemArray.forEach(el => {{
                        el.style.outline = '3px solid {color_code}';
                        el.style.outlineOffset = '2px';
                        el.style.backgroundColor = '{color_code}20';
                        el.setAttribute('data-selector-highlighted', 'true');
                    }});
                }}
                """
            )

            self.highlighted_selectors.add(selector)
            return count

        except Exception:
            return 0

    def is_active(self) -> bool:
        """Check if any highlights are currently active"""
        return len(self.highlighted_selectors) > 0

    def get_highlighted_count(self) -> int:
        """Get number of highlighted selectors"""
        return len(self.highlighted_selectors)
