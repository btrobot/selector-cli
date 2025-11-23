"""
Location Strategy Engine

Core engine that finds the optimal locator (CSS or XPath) for an element
using multi-strategy approach with uniqueness verification.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from src.core.element import Element
from src.core.locator.cost import calculate_total_cost, STRATEGY_COSTS, CostCalculator
from src.core.locator.validator import UniquenessValidator


class LocatorType(Enum):
    """Type of locator"""
    CSS = "css"
    XPATH = "xpath"


class StrategyPriority(Enum):
    """Strategy priority levels (lower value = higher priority)"""

    # P0: Optimal strategies (cost < 0.15)
    ID_SELECTOR = 1  # #element-id
    DATA_TESTID = 2  # [data-testid="value"]
    LABEL_FOR = 3    # label[for="id"] + input
    TYPE_NAME_PLACEHOLDER = 4  # input[type][name][placeholder]
    HREF = 5         # a[href="/url"]

    # P1: Excellent strategies (cost 0.15-0.25)
    TYPE_NAME = 10        # input[type][name]
    TYPE_PLACEHOLDER = 11  # input[type][placeholder]
    ARIA_LABEL = 12       # [aria-label="value"]
    XPATH_ID = 13         # //tag[@id="value"]

    # P2: Good strategies (cost 0.25-0.40)
    TITLE_ATTR = 20       # [title="value"]
    CLASS_UNIQUE = 21     # .single-class
    NTH_OF_TYPE = 22      # tag:nth-of-type(n)
    XPATH_ATTR = 23       # //tag[@attr="value"]

    # P3: Fallback strategies (cost > 0.40)
    TEXT_CONTENT = 30     # :has-text("text")
    XPATH_TEXT = 31       # //tag[contains(text(), "text")]
    TYPE_ONLY = 32        # tag[type="value"]
    XPATH_POSITION = 33   # /html/body/tag[1]

    @property
    def level(self) -> int:
        """Get priority level for grouping"""
        if self.value <= 5:
            return 0  # P0
        elif self.value <= 13:
            return 1  # P1
        elif self.value <= 23:
            return 2  # P2
        else:
            return 3  # P3


@dataclass
class LocationResult:
    """
    Result of location strategy execution

    Attributes:
        type: 'css' or 'xpath'
        selector: The locator string
        strategy: Name of the strategy used
        cost: Computed cost (lower is better)
        is_unique: Whether selector is guaranteed unique
        fallback_selectors: List of alternative selectors
        warnings: Any warnings about the locator
    """

    type: LocatorType
    selector: str
    strategy: str
    cost: float
    is_unique: bool = True
    fallback_selectors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize optional fields"""
        if self.fallback_selectors is None:
            self.fallback_selectors = []
        if self.warnings is None:
            self.warnings = []


class LocationStrategyEngine:
    """Engine for finding optimal element locators"""

    def __init__(self):
        # Initialize components
        self.validator = UniquenessValidator()
        self.cost_calculator = CostCalculator()
        self.css_strategies = self._load_css_strategies()
        self.xpath_strategies = self._load_xpath_strategies()
        self._cache = {}  # For caching validation results

    def _load_css_strategies(self) -> List[Dict[str, Any]]:
        """Load CSS strategy definitions"""
        return [
            # P0: Optimal strategies
            {
                'name': 'ID_SELECTOR',
                'priority': StrategyPriority.ID_SELECTOR,
                'generator': self._generate_id_selector,
                'applies_to': ['input', 'button', 'a', 'select', 'textarea', '*'],
            },
            {
                'name': 'DATA_TESTID',
                'priority': StrategyPriority.DATA_TESTID,
                'generator': self._generate_data_testid_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'LABEL_FOR',
                'priority': StrategyPriority.LABEL_FOR,
                'generator': self._generate_label_for_selector,
                'applies_to': ['input', 'select', 'textarea'],
            },
            {
                'name': 'TYPE_NAME_PLACEHOLDER',
                'priority': StrategyPriority.TYPE_NAME_PLACEHOLDER,
                'generator': self._generate_type_name_placeholder_selector,
                'applies_to': ['input'],
            },
            {
                'name': 'HREF',
                'priority': StrategyPriority.HREF,
                'generator': self._generate_href_selector,
                'applies_to': ['a'],
            },
            # P1: Excellent strategies
            {
                'name': 'TYPE_NAME',
                'priority': StrategyPriority.TYPE_NAME,
                'generator': self._generate_type_name_selector,
                'applies_to': ['input', 'button'],
            },
            {
                'name': 'TYPE_PLACEHOLDER',
                'priority': StrategyPriority.TYPE_PLACEHOLDER,
                'generator': self._generate_type_placeholder_selector,
                'applies_to': ['input'],
            },
            # P2: Good strategies
            {
                'name': 'TEXT_CONTENT',
                'priority': StrategyPriority.TEXT_CONTENT,
                'generator': self._generate_text_content_selector,
                'applies_to': ['button', 'a', 'label', '*'],
            },
        ]

    def _load_xpath_strategies(self) -> List[Dict[str, Any]]:
        """Load XPath strategy definitions"""
        return [
            {
                'name': 'XPATH_ID',
                'priority': StrategyPriority.XPATH_ID,
                'generator': self._generate_xpath_id_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'XPATH_ATTR',
                'priority': StrategyPriority.XPATH_ATTR,
                'generator': self._generate_xpath_attr_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'XPATH_TEXT',
                'priority': StrategyPriority.XPATH_TEXT,
                'generator': self._generate_xpath_text_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'XPATH_POSITION',
                'priority': StrategyPriority.XPATH_POSITION,
                'generator': self._generate_xpath_position_selector,
                'applies_to': ['*'],
            },
        ]

    # CSS Generator Methods (Placeholders - actual implementation will come later)
    def _generate_id_selector(self, element: Element) -> Optional[str]:
        """Generate ID selector: #element-id"""
        if element.id:
            return f"#{element.id}"
        return None

    def _generate_data_testid_selector(self, element: Element) -> Optional[str]:
        """Generate data-testid selector: [data-testid="value"]"""
        testid = element.attributes.get('data-testid')
        if testid:
            return f'[data-testid="{testid}"]'
        return None

    def _generate_label_for_selector(self, element: Element) -> Optional[str]:
        """Generate label-for selector"""
        if element.id:
            return f"label[for=\"{element.id}\"] + {element.tag}"
        return None

    def _generate_type_name_placeholder_selector(self, element: Element) -> Optional[str]:
        """Generate type+name+placeholder selector"""
        if element.tag == 'input' and element.type and element.name and element.placeholder:
            return f'input[type="{element.type}"][name="{element.name}"][placeholder="{element.placeholder}"]'
        return None

    def _generate_href_selector(self, element: Element) -> Optional[str]:
        """Generate href selector: a[href="/url"]"""
        if element.tag == 'a' and element.attributes.get('href'):
            return f"a[href=\"{element.attributes['href']}\"]"
        return None

    def _generate_type_name_selector(self, element: Element) -> Optional[str]:
        """Generate type+name selector"""
        if element.tag in ['input', 'button'] and element.type and element.name:
            return f'{element.tag}[type="{element.type}"][name="{element.name}"]'
        return None

    def _generate_type_placeholder_selector(self, element: Element) -> Optional[str]:
        """Generate type+placeholder selector"""
        if element.tag == 'input' and element.type and element.placeholder:
            return f'input[type="{element.type}"][placeholder="{element.placeholder}"]'
        return None

    def _generate_text_content_selector(self, element: Element) -> Optional[str]:
        """Generate text content selector: :has-text("text")"""
        if element.text:
            escaped_text = element.text.replace('"', '\\"')
            return f'{element.tag}:has-text("{escaped_text}")'
        return None

    # XPath Generator Methods
    def _generate_xpath_id_selector(self, element: Element) -> Optional[str]:
        """Generate XPath ID selector: //tag[@id="value"]"""
        if element.id:
            return f'//{element.tag}[@id="{element.id}"]'
        return None

    def _generate_xpath_attr_selector(self, element: Element) -> Optional[str]:
        """Generate XPath attribute selector"""
        conditions = []
        if element.type:
            conditions.append(f'@type="{element.type}"')
        if element.name:
            conditions.append(f'@name="{element.name}"')

        if conditions:
            return f'//{element.tag}[{" and ".join(conditions)}]'
        return None

    def _generate_xpath_text_selector(self, element: Element) -> Optional[str]:
        """Generate XPath text selector"""
        if element.text:
            return f'//{element.tag}[contains(text(), "{element.text}")]'
        return None

    def _generate_xpath_position_selector(self, element: Element) -> Optional[str]:
        """Generate XPath position selector (last resort)"""
        return f'//{element.tag}[1]'

    async def find_best_locator(self, element: Element, page) -> Optional[LocationResult]:
        """
        Find the best locator for an element

        Args:
            element: Element to locate
            page: Playwright page object

        Returns:
            LocationResult with optimal locator, or None if not found
        """
        # Phase 1: Try CSS strategies in priority order
        css_result = await self._try_css_strategies(element, page)
        if css_result and css_result.is_unique:
            return css_result

        # Phase 2: Try XPath strategies
        xpath_result = await self._try_xpath_strategies(element, page)
        if xpath_result and xpath_result.is_unique:
            return xpath_result

        # Phase 3: Best effort fallback (not yet implemented)
        # This will try all strategies and return the best one
        # even if it's not unique

        return None

    async def _try_css_strategies(self, element: Element, page) -> Optional[LocationResult]:
        """Try all CSS strategies in priority order"""
        # Get strategies that apply to this element type
        applicable_strategies = [
            s for s in self.css_strategies
            if element.tag in s['applies_to'] or '*' in s['applies_to']
        ]

        # Sort by priority (lower value = higher priority)
        applicable_strategies.sort(key=lambda s: s['priority'].value)

        attempted = []

        for strategy in applicable_strategies:
            # Generate selector
            selector = strategy['generator'](element)
            if selector is None:
                continue

            # Try to validate uniqueness (simplified - needs async)
            # This is a placeholder - actual validation needs page access
            is_unique = await self._validate_selector(selector, element, page)

            if is_unique:
                # Calculate cost
                cost = calculate_total_cost(STRATEGY_COSTS[strategy['name']], selector)

                return LocationResult(
                    type=LocatorType.CSS,
                    selector=selector,
                    strategy=strategy['name'],
                    cost=cost,
                    is_unique=True,
                )
            else:
                attempted.append({
                    'selector': selector,
                    'strategy': strategy['name'],
                    'reason': 'not_unique'
                })

        # If we get here, none were unique
        if attempted:
            # Store fallbacks for future use
            pass

        return None

    async def _try_xpath_strategies(self, element: Element, page) -> Optional[LocationResult]:
        """Try all XPath strategies in priority order"""
        applicable_strategies = [
            s for s in self.xpath_strategies
            if element.tag in s['applies_to'] or '*' in s['applies_to']
        ]

        applicable_strategies.sort(key=lambda s: s['priority'].value)

        for strategy in applicable_strategies:
            selector = strategy['generator'](element)
            if selector is None:
                continue

            # Validate uniqueness (placeholder - needs async)
            is_unique = await self._validate_selector(selector, element, page, is_xpath=True)

            if is_unique:
                cost = calculate_total_cost(STRATEGY_COSTS[strategy['name']], selector)

                return LocationResult(
                    type=LocatorType.XPATH,
                    selector=selector,
                    strategy=strategy['name'],
                    cost=cost,
                    is_unique=True,
                )

        return None

    async def _validate_selector(self, selector: str, element: Element, page, is_xpath: bool = False) -> bool:
        """
        Validate that selector uniquely identifies the element

        Uses strict uniqueness validation (Level 3) which verifies:
        1. Selector matches exactly one element on the page
        2. The matched element is the target element

        Args:
            selector: CSS or XPath selector string
            element: Target element to validate against
            page: Playwright page object
            is_xpath: True if selector is XPath, False if CSS

        Returns:
            True if selector uniquely identifies the target element
        """
        return await self.validator.is_strictly_unique(selector, element, page, is_xpath)
