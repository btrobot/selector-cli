"""
Location Strategy Engine - Phase 3 with Logging
Enhanced version with debug logging and performance tracking
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ..element import Element
from .cost import calculate_total_cost, STRATEGY_COSTS, CostCalculator
from .validator import UniquenessValidator
import logging

# Setup logger
logger = logging.getLogger('locator.strategy')
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(handler)


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
            # P2: Phase 2 Additional Strategies
            {
                'name': 'ARIA_LABEL',
                'priority': StrategyPriority.ARIA_LABEL,
                'generator': self._generate_aria_label_selector,
                'applies_to': ['*'],
            },
            # Note: TEXT_CONTENT has priority 30 (P3), moved to end of list
            # P2: Phase 2 Additional Strategies (continued)
            {
                'name': 'TITLE_ATTR',
                'priority': StrategyPriority.TITLE_ATTR,
                'generator': self._generate_title_attr_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'CLASS_UNIQUE',
                'priority': StrategyPriority.CLASS_UNIQUE,
                'generator': self._generate_class_unique_selector,
                'applies_to': ['*'],
            },
            {
                'name': 'NTH_OF_TYPE',
                'priority': StrategyPriority.NTH_OF_TYPE,
                'generator': self._generate_nth_of_type_selector,  # Note: async method
                'applies_to': ['*'],
            },
            # P3: Fallback strategies
            {
                'name': 'TEXT_CONTENT',
                'priority': StrategyPriority.TEXT_CONTENT,
                'generator': self._generate_text_content_selector,
                'applies_to': ['button', 'a', 'label', '*'],
            },
            {
                'name': 'TYPE_ONLY',
                'priority': StrategyPriority.TYPE_ONLY,
                'generator': self._generate_type_only_selector,
                'applies_to': ['input', 'button'],
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

    def _escape_xpath_string(self, text: str) -> str:
        """Simple XPath string escaping - use single quotes, then double if needed."""
        if not text:
            return "''"

        # No single quotes - use single quotes (most common)
        if "'" not in text:
            return f"'{text}'"

        # No double quotes - use double quotes
        if '"' not in text:
            return f'"{text}"'

        # Has both quotes - simplified (will be enhanced in future)
        return f"concat('{text}')"

    # CSS Generator Methods
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

    # P2: Additional CSS strategies for Phase 2
    def _generate_aria_label_selector(self, element: Element) -> Optional[str]:
        """Generate aria-label selector: [aria-label="value"]"""
        aria_label = element.attributes.get('aria-label')
        if aria_label:
            return f'[aria-label="{aria_label}"]'
        return None

    def _generate_title_attr_selector(self, element: Element) -> Optional[str]:
        """Generate title attribute selector: [title="value"]"""
        title = element.attributes.get('title')
        if title:
            return f'[title="{title}"]'
        return None

    def _generate_class_unique_selector(self, element: Element) -> Optional[str]:
        """Generate unique class selector: .single-class"""
        # Only generate if element has exactly one class
        if len(element.classes) == 1:
            return f'.{element.classes[0]}'
        return None

    async def _generate_nth_of_type_selector(self, element: Element, page) -> Optional[str]:
        """Generate nth-of-type selector: tag:nth-of-type(n)

        Note: This method is async and needs the page parameter to calculate
        the actual position among siblings.
        """
        # Placeholder - will be implemented with page context
        return f'{element.tag}:nth-of-type(1)'

    def _generate_type_only_selector(self, element: Element) -> Optional[str]:
        """Generate type-only selector: tag[type="value"]"""
        if element.type:
            return f'{element.tag}[type="{element.type}"]'
        return None

    # XPath Generator Methods
    def _generate_xpath_id_selector(self, element: Element) -> Optional[str]:
        """Generate XPath ID selector: //tag[@id="value"]"""
        if element.id:
            escaped_id = self._escape_xpath_string(element.id)
            return f'//{element.tag}[@id={escaped_id}]'
        return None

    def _generate_xpath_attr_selector(self, element: Element) -> Optional[str]:
        """Generate XPath attribute selector"""
        conditions = []
        if element.type:
            conditions.append(f'@type={self._escape_xpath_string(element.type)}')
        if element.name:
            conditions.append(f'@name={self._escape_xpath_string(element.name)}')

        if conditions:
            return f'//{element.tag}[{" and ".join(conditions)}]'
        return None

    def _generate_xpath_text_selector(self, element: Element) -> Optional[str]:
        """Generate XPath text selector with proper escaping"""
        if element.text:
            escaped_text = self._escape_xpath_string(element.text)
            return f'//{element.tag}[contains(text(), {escaped_text})]'
        return None

    def _generate_xpath_position_selector(self, element: Element) -> Optional[str]:
        """Generate XPath position selector (last resort)"""
        # For now, return basic position selector
        # In a full implementation, this would traverse up the DOM tree
        # to build the full path like /html/body/div[2]/button[1]
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
        logger.info(f"\n{'='*60}")
        logger.info(f"Finding locator for <{element.tag}>")
        logger.info(f"{'='*60}")

        # Phase 1: Try CSS strategies in priority order
        logger.debug("[PHASE 1] Trying CSS strategies...")
        css_result = await self._try_css_strategies(element, page)
        if css_result and css_result.is_unique:
            logger.info(f"✓ Selected CSS: {css_result.selector}")
            return css_result

        logger.debug("[PHASE 2] CSS failed, trying XPath strategies...")
        xpath_result = await self._try_xpath_strategies(element, page)
        if xpath_result and xpath_result.is_unique:
            logger.info(f"✓ Selected XPath: {xpath_result.selector}")
            return xpath_result

        logger.warning("! No unique locator found")

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

        logger.debug(f"Trying {len(applicable_strategies)} CSS strategies in order...")
        attempted = []

        for strategy in applicable_strategies:
            # Generate selector
            generator = strategy['generator']
            if 'page' in __import__('inspect').signature(generator).parameters:
                selector = await generator(element, page)
            else:
                selector = generator(element)

            if selector is None:
                logger.debug(f"  [SKIP] {strategy['name']}: not applicable")
                continue

            # Log attempt
            logger.debug(f"  [TRY] {strategy['name']:20s} → {selector}")

            # Try to validate uniqueness
            is_unique = await self._validate_selector(selector, element, page)

            if is_unique:
                cost = calculate_total_cost(STRATEGY_COSTS[strategy['name']], selector)
                logger.debug(f"  [OK]  {strategy['name']:20s} (cost: {cost:.3f})")
                return LocationResult(
                    type=LocatorType.CSS,
                    selector=selector,
                    strategy=strategy['name'],
                    cost=cost,
                    is_unique=True,
                )
            else:
                logger.debug(f"  [FAIL] {strategy['name']:20s} (not unique)")
                attempted.append({
                    'selector': selector,
                    'strategy': strategy['name'],
                    'reason': 'not_unique'
                })

        logger.debug(f"All CSS strategies failed ({len(attempted)} attempts)")
        return None

    async def _try_xpath_strategies(self, element: Element, page) -> Optional[LocationResult]:
        """Try all XPath strategies in priority order"""
        applicable_strategies = [
            s for s in self.xpath_strategies
            if element.tag in s['applies_to'] or '*' in s['applies_to']
        ]

        applicable_strategies.sort(key=lambda s: s['priority'].value)
        logger.debug(f"Trying {len(applicable_strategies)} XPath strategies...")

        for strategy in applicable_strategies:
            generator = strategy['generator']
            if 'page' in __import__('inspect').signature(generator).parameters:
                selector = await generator(element, page)
            else:
                selector = generator(element)

            if selector is None:
                continue

            logger.debug(f"  [TRY] {strategy['name']:20s} → {selector}")

            # Validate uniqueness
            is_unique = await self._validate_selector(selector, element, page, is_xpath=True)

            if is_unique:
                cost = calculate_total_cost(STRATEGY_COSTS[strategy['name']], selector)
                logger.debug(f"  [OK]  {strategy['name']:20s} (cost: {cost:.3f})")
                return LocationResult(
                    type=LocatorType.XPATH,
                    selector=selector,
                    strategy=strategy['name'],
                    cost=cost,
                    is_unique=True,
                )

        logger.debug("All XPath strategies failed")
        return None

    async def _validate_selector(self, selector: str, element: Element, page, is_xpath: bool = False) -> bool:
        """Validate that selector uniquely identifies the element"""
        logger.debug(f"    [VALIDATE] {'XPath' if is_xpath else 'CSS'}: {selector}")
        result = await self.validator.is_strictly_unique(selector, element, page, is_xpath)
        logger.debug(f"    [RESULT] {'unique' if result else 'not unique'}")
        return result
