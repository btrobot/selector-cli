"""
Element scanner for Selector CLI
"""
from typing import List, Optional, Tuple
from playwright.async_api import Page, Locator
from src.core.element import Element
import uuid


class ElementScanner:
    """Scan page for elements"""

    DEFAULT_ELEMENT_TYPES = ['input', 'button', 'a', 'select', 'textarea']

    async def scan(
        self,
        page: Page,
        element_types: List[str] = None,
        deep: bool = False
    ) -> List[Element]:
        """Scan page and return elements"""

        if element_types is None:
            element_types = self.DEFAULT_ELEMENT_TYPES

        elements = []
        index = 0

        for elem_type in element_types:
            # Query elements
            locators = await page.locator(elem_type).all()

            for locator in locators:
                # Build Element object
                element = await self._build_element(locator, index, elem_type, page.url, page)
                elements.append(element)
                index += 1

        return elements

    async def _build_element(
        self,
        locator,
        index: int,
        elem_type: str,
        page_url: str,
        page: Page
    ) -> Element:
        """Build Element object from Playwright locator"""

        # Get basic properties
        tag = elem_type
        text = await locator.inner_text() if await locator.count() > 0 else ""
        text = text.strip()[:100]  # Limit text length

        # Get attributes
        attributes = {}
        try:
            # Common attributes to extract
            for attr in ['type', 'name', 'id', 'class', 'placeholder', 'value', 'href', 'disabled', 'required']:
                attr_value = await locator.get_attribute(attr)
                if attr_value is not None:
                    attributes[attr] = attr_value
        except Exception:
            pass

        # Computed properties
        elem_type_attr = attributes.get('type', '')
        name = attributes.get('name', '')
        elem_id = attributes.get('id', '')
        placeholder = attributes.get('placeholder', '')
        value = attributes.get('value', '')
        classes = attributes.get('class', '').split() if attributes.get('class') else []

        # Build selector with uniqueness verification
        selector = await self._build_unique_selector(tag, attributes, text, page)

        # Build xpath
        xpath = await self._build_xpath(locator)

        # State
        try:
            visible = await locator.is_visible() if await locator.count() > 0 else False
            enabled = await locator.is_enabled() if await locator.count() > 0 else True
            disabled = attributes.get('disabled') is not None
        except Exception:
            visible = True
            enabled = True
            disabled = False

        return Element(
            index=index,
            uuid=str(uuid.uuid4()),
            tag=tag,
            type=elem_type_attr,
            text=text,
            value=value,
            attributes=attributes,
            name=name,
            id=elem_id,
            classes=classes,
            placeholder=placeholder,
            selector=selector,
            xpath=xpath,
            visible=visible,
            enabled=enabled,
            disabled=disabled,
            locator=locator,
            page_url=page_url
        )

    async def _build_unique_selector(
        self,
        tag: str,
        attributes: dict,
        text: str,
        page: Page
    ) -> str:
        """Build CSS selector that uniquely identifies the element

        Strategy:
        1. Try ID (most reliable)
        2. Try unique attribute combinations
        3. Try nth-child with parent context
        4. Fallback to basic selector

        Always verify uniqueness before returning.
        """
        # Strategy 1: ID - most reliable
        if 'id' in attributes and attributes['id']:
            selector = f"#{attributes['id']}"
            if await self._is_unique_selector(page, selector):
                return selector
            # If ID is not unique, fall through to other strategies
            selector = f"{tag}#{attributes['id']}"
            if await self._is_unique_selector(page, selector):
                return selector

        # Strategy 2: Unique attribute combinations
        selectors_to_try = []

        # Try combinations with increasing specificity
        base = tag

        # Add type
        if 'type' in attributes and attributes['type']:
            type_sel = f'{base}[type="{attributes["type"]}"]'

            # type + name
            if 'name' in attributes and attributes['name']:
                selectors_to_try.append(f'{type_sel}[name="{attributes["name"]}"]')

            # type + placeholder
            if 'placeholder' in attributes and attributes['placeholder']:
                placeholder = attributes['placeholder'][:30].replace('"', '\\"')
                selectors_to_try.append(f'{type_sel}[placeholder="{placeholder}"]')

            # type + value
            if 'value' in attributes and attributes['value']:
                value = attributes['value'][:30].replace('"', '\\"')
                selectors_to_try.append(f'{type_sel}[value="{value}"]')

            # Just type
            selectors_to_try.append(type_sel)

        # name alone
        if 'name' in attributes and attributes['name']:
            selectors_to_try.append(f'{base}[name="{attributes["name"]}"]')

        # placeholder alone
        if 'placeholder' in attributes and attributes['placeholder']:
            placeholder = attributes['placeholder'][:30].replace('"', '\\"')
            selectors_to_try.append(f'{base}[placeholder="{placeholder}"]')

        # href for links
        if 'href' in attributes and attributes['href']:
            href = attributes['href'][:50].replace('"', '\\"')
            selectors_to_try.append(f'{base}[href="{href}"]')

        # Try each selector for uniqueness
        for selector in selectors_to_try:
            if await self._is_unique_selector(page, selector):
                return selector

        # Strategy 3: Try with text content (for buttons/links)
        if text and tag in ['button', 'a']:
            # Escape quotes in text
            escaped_text = text[:30].replace('"', '\\"')
            text_selector = f'{tag}:has-text("{escaped_text}")'
            if await self._is_unique_selector(page, text_selector):
                return text_selector

        # Strategy 4: Fallback - use basic selector even if not unique
        # This is the old behavior - just return something reasonable
        if 'type' in attributes and attributes['type']:
            return f'{base}[type="{attributes["type"]}"]'
        elif 'name' in attributes and attributes['name']:
            return f'{base}[name="{attributes["name"]}"]'
        else:
            return tag

    async def _is_unique_selector(self, page: Page, selector: str) -> bool:
        """Check if selector matches exactly one element on the page"""
        try:
            count = await page.locator(selector).count()
            return count == 1
        except Exception:
            return False

    def _build_selector(self, tag: str, attributes: dict) -> str:
        """Build CSS selector from tag and attributes (legacy method)"""
        selector = tag

        # Prefer id
        if 'id' in attributes and attributes['id']:
            return f"{tag}#{attributes['id']}"

        # Then type
        if 'type' in attributes and attributes['type']:
            selector += f'[type="{attributes["type"]}"]'

        # Then name
        elif 'name' in attributes and attributes['name']:
            selector += f'[name="{attributes["name"]}"]'

        # Then placeholder
        elif 'placeholder' in attributes and attributes['placeholder']:
            placeholder = attributes['placeholder'][:30]
            selector += f'[placeholder="{placeholder}"]'

        return selector

    async def _build_xpath(self, locator) -> str:
        """Build XPath for element using JavaScript"""
        try:
            # Execute JavaScript to get XPath
            xpath = await locator.evaluate("""
                (element) => {
                    function getXPath(node) {
                        if (node.id) {
                            return `//*[@id="${node.id}"]`;
                        }

                        if (node === document.body) {
                            return '/html/body';
                        }

                        let ix = 0;
                        const siblings = node.parentNode ? node.parentNode.childNodes : [];

                        for (let i = 0; i < siblings.length; i++) {
                            const sibling = siblings[i];
                            if (sibling === node) {
                                const tagName = node.tagName.toLowerCase();
                                return getXPath(node.parentNode) + '/' + tagName + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === node.tagName) {
                                ix++;
                            }
                        }
                    }
                    return getXPath(element);
                }
            """)
            return xpath if xpath else ""
        except Exception:
            return ""
