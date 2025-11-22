"""
Element scanner for Selector CLI
"""
from typing import List
from playwright.async_api import Page
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
                element = await self._build_element(locator, index, elem_type, page.url)
                elements.append(element)
                index += 1

        return elements

    async def _build_element(
        self,
        locator,
        index: int,
        elem_type: str,
        page_url: str
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

        # Build selector
        selector = self._build_selector(tag, attributes)

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

    def _build_selector(self, tag: str, attributes: dict) -> str:
        """Build CSS selector from tag and attributes"""
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
