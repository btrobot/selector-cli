# Element Location Strategy - Implementation Plan

**Plan Version**: 1.0
**Created**: 2025-11-23
**Status**: Planning Phase
**Estimated Duration**: 3-4 weeks
**Team Size**: 1-2 developers

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Foundation (Week 1)](#phase-1-foundation-week-1)
3. [Phase 2: CSS Strategies (Week 2)](#phase-2-css-strategies-week-2)
4. [Phase 3: XPath & Integration (Week 3)](#phase-3-xpath-integration-week-3)
5. [Phase 4: Testing & Optimization (Week 4)](#phase-4-testing-optimization-week-4)
6. [Risk Management](#risk-management)
7. [Success Metrics](#success-metrics)
8. [Rollout Plan](#rollout-plan)

---

## Overview

### Project Goals

Implement the Element Location Strategy design to achieve:
- **95%+** unique element identification success rate
- **Zero** "strict mode violation" errors
- **Automatic** fallback to optimal selectors
- **Human-readable** selectors (CSS preferred over XPath)

### High-Level Approach

**Incremental Implementation**: Build foundation first, then add strategies layer by layer

**Testing-Driven**: Each phase includes comprehensive tests

**Backward Compatible**: Maintain existing API while adding new capabilities

### Timeline Summary

| Phase | Duration | Focus | Deliverables |
|-------|----------|-------|--------------|
| Phase 1 | 1 week | Foundation & Core Algorithm | Strategy engine, cost model, validation |
| Phase 2 | 1 week | CSS Strategy Implementation | 12 CSS strategies, element-type specific |
| Phase 3 | 1 week | XPath & Integration | 5 XPath strategies, scanner integration |
| Phase 4 | 1 week | Testing & Optimization | 80%+ coverage, performance tuning |

**Total Estimated Time**: 3-4 weeks

---

## Phase 1: Foundation (Week 1)

**Duration**: 5 days

### Objectives

- Build the core strategy engine framework
- Implement cost calculation model
- Create uniqueness validation system
- Establish testing infrastructure

### Day 1: Project Setup & Core Classes

#### Tasks

1. **Create directory structure**
   ```
   src/
   ├── core/
   │   ├── element.py          (existing, modify)
   │   ├── scanner.py          (existing, modify)
   │   └── locator/            (new)
   │       ├── __init__.py
   │       ├── strategy.py     (new)
   │       ├── cost.py         (new)
   │       └── validator.py    (new)
   tests/
   ├── unit/
   │   ├── test_strategy.py    (new)
   │   ├── test_cost.py        (new)
   │   └── test_validator.py   (new)
   └── integration/
       └── test_locator_engine.py (new)
   ```

2. **Define base classes and enums**
   - Create `LocatorType` enum (CSS, XPATH)
   - Create `LocationResult` dataclass
   - Create `Strategy` base class
   - Define `Priority` enum

3. **Setup testing infrastructure**
   - Create test fixtures for mock elements
   - Create mock page objects
   - Setup test data

#### Deliverables

- [ ] Directory structure created
- [ ] Base classes defined with type hints
- [ ] Test infrastructure ready
- [ ] Initial unit tests for base classes

#### Acceptance Criteria

- All base classes pass type checking
- Tests run successfully
- Code follows project style guidelines

#### Time Estimate

- **Development**: 4 hours
- **Testing**: 2 hours
- **Documentation**: 1 hour
- **Total**: 7 hours

### Day 2: Cost Model Implementation

#### Tasks

1. **Implement cost calculation functions**
   ```python
   # In src/core/locator/cost.py
   def calculate_base_cost(strategy: Strategy) -> float
   def calculate_length_penalty(selector: str) -> float
   def calculate_special_char_penalty(selector: str) -> float
   def calculate_index_penalty(selector: str) -> float
   def calculate_total_cost(strategy: Strategy, selector: str) -> float
   ```

2. **Define pre-computed strategy costs**
   - Create dictionary of all 17 strategies with their base costs
   - Document cost values and rationale

3. **Unit tests for cost functions**
   - Test each penalty calculation
   - Test edge cases (empty selector, very long selector)
   - Verify cost ordering (ID < Name < Text < XPath)

#### Test Cases

```python
def test_id_selector_cost():
    cost = calculate_total_cost(ID_STRATEGY, "#submit-btn")
    assert 0.05 < cost < 0.08

def test_xpath_position_cost():
    cost = calculate_total_cost(XPATH_POSITION, "/html/body/div[2]/button")
    assert cost > 0.50

def test_special_char_penalty():
    selector = '[type="email"][name="user-email"][placeholder="Enter email"]'
    penalty = calculate_special_char_penalty(selector)
    assert 0.1 < penalty < 0.2
```

#### Deliverables

- [ ] Cost calculation functions implemented
- [ ] All penalty functions tested
- [ ] Strategy cost table defined
- [ ] Cost-related unit tests passing

#### Acceptance Criteria

- Cost values follow priority order (lower cost = better strategy)
- All penalty calculations documented
- 100% code coverage for cost module

#### Time Estimate

- **Development**: 5 hours
- **Testing**: 3 hours
- **Documentation**: 1 hour
- **Total**: 9 hours

### Day 3: Uniqueness Validator

#### Tasks

1. **Implement uniqueness validation**
   ```python
   # In src/core/locator/validator.py
   async def is_unique(selector: str, page) -> bool
   async def matches_target(selector: str, target_element, page) -> bool
   async def is_strictly_unique(selector: str, target_element, page) -> bool
   ```

2. **Three-tier validation system**
   - **Level 1**: Count check (must be exactly 1)
   - **Level 2**: Attribute verification (type, name, id must match)
   - **Level 3**: Identity check (JavaScript object equality)

3. **Performance optimizations**
   - Batch validation wherever possible
   - Cache validation results
   - Parallel attribute checks

4. **Comprehensive tests**
   - Test with mock page returning multiple elements
   - Test attribute mismatch scenarios
   - Test identity check with real browser

#### Test Cases

```python
async def test_unique_selector():
    mock_page = MockPage(elements=[btn1])
    result = await is_unique("#btn1", mock_page)
    assert result is True

async def test_non_unique_selector():
    mock_page = MockPage(elements=[btn1, btn2])
    result = await is_unique("button", mock_page)
    assert result is False

async def test_selector_matches_different_element():
    # Selector matches an element, but not the target
    result = await matches_target("#wrong-id", target_btn, mock_page)
    assert result is False
```

#### Deliverables

- [ ] Validator functions implemented
- [ ] All three validation levels working
- [ ] Performance optimizations in place
- [ ] Validator tests passing

#### Acceptance Criteria

- Validator correctly identifies unique vs non-unique selectors
- All three validation levels tested
- Performance: < 10ms per validation

#### Risks & Mitigation

- **Risk**: JavaScript identity check may be slow
  - **Mitigation**: Make Level 3 validation optional
  - **Mitigation**: Use caching aggressively

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 4 hours
- **Documentation**: 1 hour
- **Total**: 11 hours

### Day 4: Strategy Engine Core

#### Tasks

1. **Implement strategy engine base class**
   ```python
   # In src/core/locator/strategy.py
   class LocationStrategyEngine:
       def __init__(self):
           self.css_strategies = self._load_css_strategies()
           self.xpath_strategies = self._load_xpath_strategies()
           self.validator = UniquenessValidator()
           self.cost_calculator = CostCalculator()

       async def find_best_locator(self, element, page) -> LocationResult:
           pass
   ```

2. **Master algorithm implementation**
   ```
   1. Try CSS strategies in priority order
   2. If unique found → return LocationResult
   3. Try XPath strategies in priority order
   4. If unique found → return LocationResult
   5. Find minimum cost alternative
   6. Return best effort result
   ```

3. **Helper methods**
   - `_try_css_strategies()`
   - `_try_xpath_strategies()`
   - `_find_minimum_cost_locator()`

4. **Error handling & logging**
   - Log each attempted strategy
   - Log why strategies failed
   - Provide debug information

5. **Integration tests**
   - Test full pipeline with mock element
   - Verify fallback mechanism works
   - Test failure scenarios

#### Test Cases

```python
async def test_find_best_locator_css_unique():
    engine = LocationStrategyEngine()
    element = create_element(id="submit-btn")

    result = await engine.find_best_locator(element, mock_page)

    assert result.type == 'css'
    assert result.selector == '#submit-btn'
    assert result.strategy == 'ID_SELECTOR'
    assert result.is_unique is True

async def test_find_best_locator_fallback():
    # Element with no unique CSS
    element = create_element(tag="button", type="button")

    result = await engine.find_best_locator(element, mock_page)

    # Should find XPath fallback
    assert result.type == 'xpath'
    assert result.is_unique is True  # Still unique

async def test_find_best_locator_non_unique():
    # Element that truly cannot be uniquely identified
    element = create_element(tag="div")  # Generic div

    result = await engine.find_best_locator(element, mock_page)

    assert result.is_unique is False  # Explicitly marked
    assert 'Fallback' in result.strategy
    assert result.warnings is not None
```

#### Deliverables

- [ ] Strategy engine class implemented
- [ ] Master algorithm working
- [ ] All fallback paths tested
- [ ] Debug logging in place
- [ ] Integration tests passing

#### Acceptance Criteria

- Engine returns LocationResult with all required fields
- CSS strategies tried before XPath
- Proper fallback when no unique CSS selector found
- Debug information available for troubleshooting

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 5 hours
- **Documentation**: 2 hours
- **Total**: 13 hours

### Day 5: Phase 1 Testing & Review

#### Tasks

1. **Complete test coverage**
   - Ensure all new code has tests
   - Target: 90%+ code coverage
   - Add edge case tests

2. **Integration testing**
   - Test engine with real browser page
   - Test on sample HTML files
   - Test performance with 100+ elements

3. **Code review & documentation**
   - Review all Phase 1 code
   - Add docstrings to all functions
   - Update README.md with locator info

4. **Create Phase 1 summary**
   - Document what works
   - Document known limitations
   - Plan Phase 2 adjustments

#### Deliverables

- [ ] Code coverage report ≥ 90%
- [ ] Integration tests with real browser
- [ ] Performance benchmark results
- [ ] Phase 1 completion report

#### Acceptance Criteria

- All tests passing
- Performance: scan 100 elements < 5 seconds
- Documentation complete
- Ready for Phase 2

#### Time Estimate

- **Testing**: 4 hours
- **Documentation**: 3 hours
- **Code Review**: 2 hours
- **Total**: 9 hours

### Phase 1 Summary

**Total Hours**: 7 + 9 + 11 + 13 + 9 = **49 hours** (~6 working days)

**Key Deliverables**:
- Core strategy engine framework
- Cost model with 17 strategies
- Uniqueness validator with 3 levels
- Fully tested foundation

**Phase 1 Complete When**: Can reliably evaluate strategies and calculate costs for any element

---

## Phase 2: CSS Strategies (Week 2)

**Duration**: 5 days

### Objectives

- Implement 12 CSS selector generation strategies
- Element-type specific optimization
- Integration with strategy engine
- Comprehensive strategy testing

### Day 1: P0 CSS Strategies

#### Tasks

Implement highest priority CSS strategies (Cost < 0.15):

1. **ID_SELECTOR strategy**
   ```python
   def generate_id_selector(element) -> Optional[str]:
       if element.id:
           return f"#{element.id}"
       return None
   ```

2. **DATA_TESTID strategy**
   ```python
   def generate_data_testid_selector(element) -> Optional[str]:
       testid = element.attributes.get('data-testid')
       if testid:
           return f'[data-testid="{testid}"]'
       return None
   ```

3. **LABEL_FOR strategy**
   ```python
   async def generate_label_for_selector(element, page) -> Optional[str]:
       # Check if element has associated label
       label = await page.locator(f'label[for="{element.id}"]').first
       if label:
           return f'label[for="{element.id}"] + input'
       return None
   ```

4. **TYPE_NAME_PLACEHOLDER strategy**
   ```python
   def generate_type_name_placeholder_selector(element) -> Optional[str]:
       if element.tag == 'input' and element.type and element.name and element.placeholder:
           return f'input[type="{element.type}"][name="{element.name}"][placeholder="{element.placeholder}"]'
       return None
   ```

5. **HREF strategy**
   ```python
   def generate_href_selector(element) -> Optional[str]:
       if element.tag == 'a' and element.attributes.get('href'):
           return f"a[href=\"{element.attributes['href']}\"]"
       return None
   ```

6. **Unit tests for each strategy**
   - Test element with attribute → returns selector
   - Test element without attribute → returns None
   - Test selector generation format

#### Test Cases

```python
def test_id_selector_success():
    element = MockElement(id="submit-btn")
    result = generate_id_selector(element)
    assert result == "#submit-btn"

def test_id_selector_none():
    element = MockElement(id="")
    result = generate_id_selector(element)
    assert result is None

def test_data_testid_selector():
    element = MockElement(attributes={"data-testid": "submit-button"})
    result = generate_data_testid_selector(element)
    assert result == '[data-testid="submit-button"]'

def test_type_name_placeholder_selector():
    element = MockElement(
        tag="input",
        type="email",
        name="user-email",
        placeholder="Enter your email"
    )
    result = generate_type_name_placeholder_selector(element)
    assert 'type="email"' in result
    assert 'name="user-email"' in result
    assert 'placeholder="Enter your email"' in result
```

#### Deliverables

- [ ] 5 P0 CSS strategy generators implemented
- [ ] Unit tests for each strategy
- [ ] Integration with strategy engine
- [ ] All tests passing

#### Acceptance Criteria

- Each strategy correctly generates selector or returns None
- Strategies integrated into engine's CSS list
- 100% code coverage for strategy generators

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 4 hours
- **Total**: 10 hours

### Day 2: P1 CSS Strategies

#### Tasks

Implement high-priority CSS strategies (Cost 0.15-0.25):

1. **TYPE_NAME strategy**
   - `button[type="submit"][name="submit-btn"]`

2. **TYPE_PLACEHOLDER strategy**
   - `input[type="email"][placeholder="Email"]`

3. **ARIA_LABEL strategy**
   - `[aria-label="Submit form"]`

4. **XPATH_ID strategy** (note: CSS-like XPath for attributes)
   - Actually generates CSS: `*[@id="email"]` (CSS4)

5. **Unit tests for each strategy**
   - Test various combinations
   - Test attribute escaping

#### Special Considerations

- **ARIA_LABEL**: Works for any element type
- **TYPE_NAME**: Most common for form elements
- **Escaping**: Handle quotes in attributes

#### Test Cases

```python
def test_aria_label_selector():
    element = MockElement(attributes={"aria-label": "Close dialog"})
    result = generate_aria_label_selector(element)
    assert result == '[aria-label="Close dialog"]'

def test_attribute_escaping():
    element = MockElement(placeholder='Email with "quotes"')
    result = generate_type_placeholder_selector(element)
    assert '\\"' in result or '"' in result  # Properly escaped
```

#### Deliverables

- [ ] 4 P1 CSS strategies implemented
- [ ] Escaping logic for special characters
- [ ] Tests for all strategies

#### Acceptance Criteria

- Escaping handles special characters correctly
- All P1 strategies integrated
- Tests verify escaping behavior

#### Time Estimate

- **Development**: 5 hours
- **Testing**: 3 hours
- **Total**: 8 hours

### Day 3: P2 CSS Strategies

#### Tasks

Implement medium-priority CSS strategies (Cost 0.25-0.40):

1. **TITLE_ATTR strategy**
   - `button[title="Submit form"]`

2. **CLASS_UNIQUE strategy**
   - `button.btn-primary` (only when single unique class)
   - **Important**: Verify class doesn't contain numbers (dynamic)

3. **NTH_OF_TYPE strategy**
   - `button:nth-of-type(2)`
   - **Important**: Only use when parent is stable

4. **Implementation considerations**
   - CLASS_UNIQUE: Check parent context for stability
   - NTH_OF_TYPE: Only if parent has stable ID or is body

5. **Tests for dynamic attribute detection**
   - Class with numbers: `item-123` → skip
   - Class with timestamp: `active-1612345678` → skip

#### Test Cases

```python
def test_class_unique_skips_dynamic():
    element = MockElement(classes=["item-123", "active"])
    result = generate_class_unique_selector(element)
    # Should skip "item-123" because it has numbers
    assert "item-123" not in result if result else True

def test_nth_of_type_with_stable_parent():
    element = MockElement(tag="button" )
    parent = MockElement(id="form-container")  # Stable parent
    result = generate_nth_of_type_selector(element, parent)
    assert result is not None

def test_nth_of_type_with_unstable_parent():
    element = MockElement(tag="button")
    parent = MockElement()  # No stable attributes
    result = generate_nth_of_type_selector(element, parent)
    assert result is None  # Should not use nth-of-type
```

#### Deliverables

- [ ] 3 P2 CSS strategies implemented
- [ ] Dynamic class detection logic
- [ ] Parent stability checking
- [ ] Tests for edge cases

#### Acceptance Criteria

- Dynamic classes (with numbers) are correctly identified
- nth-of-type only suggested for stable parents
- All edge cases covered by tests

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 4 hours
- **Total**: 10 hours

### Day 4: Element-Type Optimization

#### Tasks

1. **Create strategy mappings per element type**

   ```python
   CSS_STRATEGIES_BY_TYPE = {
       'input': [ID, LABEL_FOR, TYPE_NAME_PLACEHOLDER, TYPE_NAME, TYPE_PLACEHOLDER, ...],
       'button': [ID, TEXT_CONTENT, ARIA_LABEL, TYPE_ONLY, CLASS_UNIQUE, ...],
       'a': [HREF, TEXT_CONTENT, ID, ARIA_LABEL, TITLE_ATTR, ...],
       'select': [ID, NAME, LABEL_FOR, TYPE_NAME, ...],
       'textarea': [ID, NAME, PLACEHOLDER, LABEL_FOR, ...],
   }
   ```

2. **Element-type specific generators**
   - `generate_input_strategies()`
   - `generate_button_strategies()`
   - `generate_link_strategies()`

3. **Reordering by element type**
   - Checkbox inputs: prioritize type+name
   - Submit buttons: prioritize text content
   - Navigation links: prioritize href

4. **Integration testing**
   - Test engine picks correct strategies by type
   - Verify priority ordering per type

5. **Documentation**
   - Document strategy ordering per type
   - Explain rationale for ordering

#### Test Cases

```python
def test_input_strategy_priority():
    element = create_element(tag="input", id="email", name="user-email")

    result = strategy_engine.find_best_locator(element, page)

    # Should pick ID over name
    assert result.strategy == 'ID_SELECTOR'

def test_button_text_priority():
    element = create_element(tag="button", text="Submit", type="submit")

    result = strategy_engine.find_best_locator(element, page)

    # Text should be tried before type-only
    if result.strategy == 'TEXT_CONTENT':
        assert 'has-text' in result.selector
```

#### Deliverables

- [ ] Strategy mappings per element type
- [ ] Element-type specific generators
- [ ] Integration tests for type-specific behavior
- [ ] Documentation of type-specific priorities

#### Acceptance Criteria

- Different element types use different strategy orderings
- Engine correctly routes to type-specific generators
- Tests verify type-specific behavior

#### Time Estimate

- **Development**: 5 hours
- **Testing**: 3 hours
- **Documentation**: 2 hours
- **Total**: 10 hours

### Day 5: Phase 2 Integration Testing

#### Tasks

1. **Comprehensive CSS strategy tests**
   - Test all 12 strategies with real elements
   - Test strategy ordering per type
   - Test fallback behavior

2. **Real browser testing**
   - Test on sample HTML page
   - Test on popular websites (GitHub, Amazon)
   - Record success rates per strategy

3. **Performance testing**
   - Measure strategy generation time
   - Measure validation time
   - Verify caching works

4. **Bug fixes & polish**
   - Fix any issues found
   - Improve error messages
   - Add debug logging

5. **Phase 2 review**
   - Review all CSS strategies
   - Document limitations
   - Prepare for Phase 3

#### Test Cases

```python
# Real-world test
async def test_github_signin_page():
    page = await open_page("https://github.com/login")
    scanner = ElementScanner()
    elements = await scanner.scan(page)

    # Verify high success rate
    unique_elements = sum(1 for e in elements if e.locator_cost < 0.4)
    assert unique_elements / len(elements) > 0.9

    # Check specific elements
    email_inputs = [e for e in elements if e.type == 'email']
    assert all(e.locator_strategy in ['ID', 'TYPE_NAME_PLACEHOLDER']
               for e in email_inputs)
```

#### Deliverables

- [ ] All 12 CSS strategies tested with real elements
- [ ] Integration tests with real browser
- [ ] Performance benchmarks
- [ ] Phase 2 completion report
- [ ] Bug fixes from testing

#### Acceptance Criteria

- 90%+ success rate on real websites
- Average cost < 0.25 for identified elements
- Performance within targets
- Ready for XPath implementation

#### Time Estimate

- **Testing**: 6 hours
- **Bug fixes**: 3 hours
- **Documentation**: 2 hours
- **Review**: 1 hour
- **Total**: 12 hours

### Phase 2 Summary

**Total Hours**: 10 + 8 + 10 + 10 + 12 = **50 hours** (~6 working days)

**Key Deliverables**:
- 12 CSS strategies fully implemented
- Element-type specific optimization
- Tested on real websites
- 90%+ success rate achieved

**Phase 2 Complete When**: All common elements can be located with CSS selectors

---

## Phase 3: XPath & Integration (Week 3)

**Duration**: 5 days

### Objectives

- Implement 5 XPath selector generation strategies
- Integrate with Phase 1-2 code
- Real-world testing with complex pages
- Performance optimization

### Day 1: P3 XPath Strategies

#### Tasks

Implement fallback XPath strategies (Cost > 0.40):

1. **TEXT_CONTENT_XPATH strategy**
   ```python
   def generate_text_content_xpath(element) -> Optional[str]:
       if element.text:
           escaped = escape_xpath_string(element.text)
           return f'//{element.tag}[contains(text(), {escaped})]'
       return None
   ```

2. **XPATH_ATTR strategy**
   ```python
   def generate_xpath_attr_selector(element) -> Optional[str]:
       conditions = []
       if element.type:
           conditions.append(f'@type={escape_xpath_string(element.type)}')
       if element.name:
           conditions.append(f'@name={escape_xpath_string(element.name)}')

       if conditions:
           return f'//{element.tag}[{" and ".join(conditions)}]'
       return None
   ```

3. **XPATH_POSITION strategy** (last resort)
   ```python
   def generate_xpath_position_selector(element) -> str:
       # Full path generation
       path = []
       current = element

       while current:
           index = get_element_index(current)
           path.insert(0, f"{current.tag}[{index}]")
           current = current.parent

       return "/" + "/".join(path)
   ```

4. **XPath escaping utilities**
   - Handle quotes in XPath strings
   - Handle special XPath characters
   - Handle namespaces (if needed)

5. **Unit tests for XPath generation**
   - Test escaping
   - Test attribute combinations
   - Test position calculation

#### Test Cases

```python
def test_xpath_text_escaping():
    element = MockElement(tag="button", text='Click "Me"')
    result = generate_text_content_xpath(element)
    # Should properly escape quotes
    assert 'concat(' in result or '&quot;' in result

def test_xpath_attr_multiple():
    element = MockElement(tag="input", type="email", name="email")
    result = generate_xpath_attr_selector(element)
    assert '@type' in result
    assert '@name' in result
    assert 'and' in result

def test_xpath_position():
    element = MockElement(tag="button")
    # Mock parent hierarchy
    result = generate_xpath_position_selector(element)
    assert result.startswith('/')
    assert '/button[' in result
```

#### Deliverables

- [ ] 3 XPath strategies implemented
- [ ] XPath escaping utilities
- [ ] Position calculation logic
- [ ] XPath generation tests

#### Acceptance Criteria

- XPath selectors properly escape strings
- Position calculation handles parent hierarchy
- Tests verify escaping and generation

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 4 hours
- **Total**: 10 hours

### Day 2: XPath Priority & Cost Integration

#### Tasks

1. **Assign costs to XPath strategies**
   ```python
   XPATH_STRATEGY_COSTS = {
       'XPATH_ID': 0.24,
       'XPATH_TEXT': 0.36,
       'XPATH_ATTR': 0.31,
       'XPATH_POSITION': 0.57,
   }
   ```

2. **Strategy ordering within XPath**
   - Try IDs first (cost 0.24)
   - Then attributes (cost 0.31)
   - Then text (cost 0.36)
   - Finally position (cost 0.57)

3. **Hybrid CSS/XPath strategies**
   - Some "XPath" strategies might generate CSS4 selectors
   - Example: `*[@id="email"]` works in some browsers

4. **Integration with cost calculator**
   - Handle both CSS and XPath selector costs
   - Apply same penalties (length, special chars) to XPath
   - XPath special chars: `//`, `@`, `[`, `]`, `position()`

5. **Tests for cost consistency**
   - Verify XPath IDs cheaper than full XPath
   - Verify position-based most expensive

#### Test Cases

```python
def test_xpath_id_vs_position_cost():
    element = MockElement(id="email")

    result = strategy_engine.find_best_locator(element, mock_page)

    # Should prefer CSS ID over XPath ID
    if not result.css_selector:
        # If CSS not available, should try XPath ID
        assert result.strategy == 'XPATH_ID'
        assert result.cost < 0.30  # Cheaper than position

def test_position_fallback_cost():
    element = MockElement(tag="div")  # Generic element

    result = strategy_engine.find_best_locator(element, mock_page)

    # Should be last resort with high cost
    assert result.cost > 0.50
    assert 'position' in result.strategy.lower()
```

#### Deliverables

- [ ] XPath cost assignments
- [ ] XPath strategy ordering
- [ ] Hybrid strategy handling
- [ ] XPath cost calculator tests

#### Acceptance Criteria

- XPath costs reflect priority order
- Cost calculator handles XPath special characters
- CSS preferred over XPath when both available
- Tests verify cost ordering

#### Time Estimate

- **Development**: 5 hours
- **Testing**: 3 hours
- **Total**: 8 hours

### Day 3: Full Integration

#### Tasks

1. **Wire up complete pipeline**
   ```python
   class LocationStrategyEngine:
       async def find_best_locator(self, element, page):
           # 1. Try CSS strategies
           result = await self._try_css_strategies(element, page)
           if result and result.is_unique:
               return result

           # 2. Try XPath strategies
           result = await self._try_xpath_strategies(element, page)
           if result and result.is_unique:
               return result

           # 3. Best effort fallback
           return await self._find_minimum_cost_locator(element, page)
   ```

2. **Update Scanner to use engine**
   ```python
   class ElementScanner:
       async def _build_element(self, locator, index, elem_type, page_url, page):
           # ... build basic element ...

           # Use strategy engine
           location_result = await self.strategy_engine.find_best_locator(
               element, page
           )

           # Store all results
           element.best_css_selector = location_result.css_selector
           element.best_xpath = location_result.xpath
           element.locator_strategy = location_result.strategy
           element.locator_cost = location_result.cost

           # Store fallback options
           element.fallback_selectors = location_result.fallbacks

           # Legacy compatibility
           element.selector = element.best_css_selector
           element.xpath = element.best_xpath
   ```

3. **Update Highlighter to use new locators**
   ```python
   class Highlighter:
       async def highlight_elements(self, elements):
           for elem in elements:
               # Try CSS first
               locator = elem.get_locator(preferred_type='css')
               if await self.is_unique(locator, page):
                   await self.highlight(locator)
                   continue

               # Fallback to XPath
               locator = elem.get_locator(preferred_type='xpath')
               await self.highlight(locator)
   ```

4. **Integration testing**
   - Test full pipeline: scan → locate → highlight
   - Verify all components work together
   - Test backward compatibility

5. **Debug commands**
   - Add `show [index] --verbose` to display locator info
   - Add `show [index] --fallbacks` to show alternatives
   - Add `strategy-test [index]` command for debugging

#### Integration Test Cases

```python
async def test_full_scan_locate_highlight_pipeline():
    # 1. Scan page
    elements = await scanner.scan(page)

    # 2. Verify locators assigned
    for elem in elements:
        assert elem.locator_strategy is not None
        assert elem.locator_cost is not None
        assert elem.get_locator() is not None

    # 3. Try highlighting
    highlighter = Highlighter(page)
    highlight_count = await highlighter.highlight_elements(elements)

    # 4. Verify all highlighted
    assert highlight_count == len(elements)

async def test_backward_compatibility():
    element = MockElement(selector="#old-selector")

    # New fields should be populated
    assert element.best_css_selector is not None

    # Legacy fields still accessible
    assert element.selector is not None
```

#### Deliverables

- [ ] Full pipeline integration completed
- [ ] Scanner updated to use engine
- [ ] Highlighter updated to use new locators
- [ ] Debug commands implemented
- [ ] Integration tests passing

#### Acceptance Criteria

- Full pipeline works end-to-end
- Scanner populates new locator fields
- Highlighter uses new locators
- Legacy code still works
- Integration tests demonstrate full workflow

#### Time Estimate

- **Development**: 7 hours
- **Testing**: 5 hours
- **Documentation**: 2 hours
- **Total**: 14 hours

### Day 4: Real-World Testing & Bug Fixing

#### Tasks

1. **Test on complex real websites**
   - GitHub.com (complex forms, many buttons)
   - Amazon.com (dynamic content, reviews)
   - Twitter.com (infinite scroll, modal dialogs)
   - React/Angular demo apps (SPAs)

2. **Collect metrics**
   - Success rate per website (% elements with locators)
   - Average cost per element
   - CSS vs XPath usage ratio
   - Failure cases and reasons

3. **Bug fixing**
   - Fix issues found in real-world testing
   - Improve edge case handling
   - Add workarounds for specific sites

4. **Performance optimization**
   - Profile slow parts
   - Optimize validation
   - Improve caching

5. **Update CHANGELOG.md**
   - Document all changes
   - Document breaking changes if any

#### Real-World Test Checklist

```python
def test_github_login_page():
    page = await open_page("https://github.com/login")
    elements = await scanner.scan(page)

    # Metrics
    total = len(elements)
    unique = sum(1 for e in elements if e.locator_cost < 0.4)
    css_count = sum(1 for e in elements if e.best_css_selector)

    assert unique / total > 0.90  # 90%+ unique
    assert css_count / total > 0.80  # 80%+ CSS

    # Key elements should have good locators
    email_input = next(e for e in elements if e.type == 'email')
    assert email_input.locator_strategy in ['ID', 'TYPE_NAME_PLACEHOLDER']
    assert email_input.locator_cost < 0.20

def test_amazon_product_page():
    page = await open_page("https://amazon.com/product")
    elements = await scanner.scan(page)

    # Amazon has dynamic content, but should still work
    total = len(elements)
    unique = sum(1 for e in elements if e.locator_cost < 0.4)

    assert unique / total > 0.85  # At least 85% unique
```

#### Expected Metrics

| Website | Elements | Unique % | Avg Cost | CSS % | Failures |
|---------|----------|----------|----------|-------|----------|
| GitHub.com | ~50 | >90% | <0.20 | >85% | <5 |
| Amazon.com | ~100 | >85% | <0.25 | >80% | <10 |
| Twitter.com | ~80 | >85% | <0.25 | >75% | <10 |
| SPA Demo | ~60 | >95% | <0.20 | >90% | <3 |

#### Deliverables

- [ ] Test results from 4+ real websites
- [ ] Metrics collected and analyzed
- [ ] Bugs fixed from testing
- [ ] Performance optimizations implemented
- [ ] CHANGELOG updated

#### Acceptance Criteria

- >85% success rate on all tested websites
- Average cost < 0.25 across all sites
- Performance within targets
- No critical bugs

#### Risks & Mitigation

- **Risk**: Some sites use very dynamic attributes
  - **Mitigation**: Add more aggressive dynamic attribute detection
  - **Mitigation**: Increase fallback strategy priority

- **Risk**: Performance issues on very large pages
  - **Mitigation**: Optimize validation batching
  - **Mitigation**: Add early termination for expensive checks

#### Time Estimate

- **Testing**: 6 hours
- **Bug fixing**: 4 hours
- **Optimization**: 3 hours
- **Documentation**: 2 hours
- **Total**: 15 hours

### Day 5: Phase 3 Review & Planning

#### Tasks

1. **Analyze real-world test results**
   - Which strategies work best?
   - Which elements fail most often?
   - What patterns cause high costs?

2. **Document findings**
   - Create strategy effectiveness report
   - Document common failure patterns
   - Suggest improvements for Phase 4

3. **Performance tuning**
   - Identify bottlenecks
   - Optimize hot paths
   - Tune cache sizes

4. **Plan Phase 4**
   - Decide which edge cases to handle
   - Plan optimization strategies
   - Set Phase 4 goals

5. **Code cleanup**
   - Remove dead code
   - Refactor duplication
   - Improve comments

6. **Create Phase 3 summary**
   - Document what works
   - Document what doesn't
   - Plan next steps

#### Deliverables

- [ ] Real-world test analysis report
- [ ] Strategy effectiveness documentation
- [ ] Performance bottlenecks identified
- [ ] Phase 4 plan
- [ ] Code cleanup completed
- [ ] Phase 3 completion report

#### Acceptance Criteria

- Real-world testing shows >85% success rate
- Performance within acceptable ranges
- Phase 4 scope clearly defined
- Code ready for optimization

#### Time Estimate

- **Analysis**: 3 hours
- **Optimization**: 3 hours
- **Documentation**: 2 hours
- **Planning**: 2 hours
- **Total**: 10 hours

### Phase 3 Summary

**Total Hours**: 10 + 8 + 14 + 15 + 10 = **57 hours** (~7 working days)

**Key Deliverables**:
- 5 XPath strategies implemented
- Full integration complete
- Real-world testing shows 85%+ success rate
- Performance optimized

**Phase 3 Complete When**: End-to-end pipeline works on real websites with good success rate

---

## Phase 4: Testing & Optimization (Week 4)

**Duration**: 5 days (may extend to 6-7 days if needed)

### Objectives

- Achieve 90%+ test coverage
- Reach 95%+ success rate on real websites
- Optimize performance to meet targets
- Handle edge cases
- Production-ready codebase

### Day 1: Test Coverage Expansion

#### Tasks

1. **Analyze current coverage**
   ```bash
   pytest --cov=src --cov-report=html
   ```

2. **Identify uncovered areas**
   - Look for edge cases not tested
   - Find error handling paths missing tests
   - Check integration test gaps

3. **Add unit tests for uncovered code**
   - Target: 90%+ coverage per module
   - Focus on:
     - Error handling branches
     - Edge cases in strategy generators
     - Validator edge cases

4. **Add integration tests**
   - Test full pipeline with various element types
   - Test fallback scenarios
   - Test error recovery

5. **Add performance tests**
   - Measure scan time for 100 elements
   - Measure locator generation time
   - Measure validation time

#### Test Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| strategy.py | ~70% | 95% |
| cost.py | ~80% | 100% |
| validator.py | ~75% | 95% |
| scanner.py | ~60% | 90% |
| **Overall** | **~70%** | **90%+** |

#### Test Cases to Add

```python
# Error handling
def test_validator_handles_stale_element():
    # Element removed from DOM during validation
    pass

def test_strategy_handles_missing_attributes():
    # Element without expected attributes
    pass

# Edge cases
def test_nth_of_type_with_removed_siblings():
    # DOM changes after scan
    pass

# Integration
def test_scan_with_multiple_pages():
    # Navigate, scan, navigate back
    pass
```

#### Deliverables

- [ ] Coverage report showing 90%+ overall
- [ ] Unit tests for all uncovered branches
- [ ] Integration tests for full pipeline
- [ ] Performance benchmark tests

#### Acceptance Criteria

- Overall coverage >= 90%
- No module with < 85% coverage
- All critical paths tested
- Performance benchmarks established

#### Time Estimate

- **Development**: 6 hours
- **Testing**: 4 hours
- **Total**: 10 hours

### Day 2: Edge Cases & Hardening

#### Tasks

1. **Identify edge cases from testing**
   - Review failing tests
   - Look for TODOs in code
   - Check error logs from real-world testing

2. **Implement edge case handling**

   ```python
   # Example: Handle elements with no identifying attributes
   async def find_best_locator(element, page):
       # ... existing logic ...

       # Edge case: element has NO good attributes
       if not result or not result.is_unique:
           result = await self._handle_generic_element(element, page)

   async def _handle_generic_element(self, element, page):
       # Use JavaScript to find stable parent
       # Generate position-based selector
       # Add warning to user
       pass
   ```

3. **Common edge cases to handle**
   - Elements without any attributes (generic div/span)
   - SVG elements (different attribute set)
   - Canvas elements (no text content)
   - Elements in iframe
   - Elements in open shadow DOM

4. **Error handling improvements**
   - Better error messages
   - Graceful degradation
   - User-friendly warnings

5. **Add tests for edge cases**
   - Each edge case should have test
   - Verify graceful degradation
   - Verify user warnings

#### Edge Cases to Handle

| Edge Case | Current Behavior | Desired Behavior | Implementation |
|-----------|-----------------|------------------|----------------|
| Generic div (no attrs) | May fail uniqueness | Use position or parent context | `_handle_generic_element()` |
| SVG elements | May create invalid CSS | Use `*` or specific SVG selectors | `is_svg_element()` check |
| Dynamic classes | May create fragile selectors | Detect and skip dynamic classes | Regex detection |
| Iframe elements | Not accessible | Switch context to iframe | `page.frame()` |
| Shadow DOM | Not supported | Pierce shadow root | `::shadow` or JS |

#### Deliverables

- [ ] Generic element handling implemented
- [ ] SVG element handling
- [ ] Dynamic class detection
- [ ] Error messages improved
- [ ] Tests for each edge case

#### Acceptance Criteria

- All identified edge cases handled
- Graceful degradation works
- User gets helpful warnings
- Tests verify edge case handling

#### Time Estimate

- **Development**: 8 hours
- **Testing**: 4 hours
- **Total**: 12 hours

### Day 3: Performance Optimization

#### Tasks

1. **Profile code to find bottlenecks**
   - Use py-spy or cProfile
   - Focus on hot paths:
     - Strategy generation
     - Uniqueness validation
     - Scanning large pages

2. **Optimization strategies**

   ```python
   # 1. Cache validation results
   class UniquenessValidator:
       def __init__(self):
           self.validation_cache = {}

       async def is_unique(self, selector, page):
           cache_key = f"{page.url}:{selector}"
           if cache_key in self.validation_cache:
               return self.validation_cache[cache_key]

           result = await self._check_uniqueness(selector, page)
           self.validation_cache[cache_key] = result
           return result

   # 2. Batch validation
   async def validate_multiple_selectors(selectors, page):
       # Run all validations in parallel
       tasks = [self.is_unique(s, page) for s in selectors]
       return await asyncio.gather(*tasks)

   # 3. Early termination
   async def try_css_strategies(self, element, page):
       for strategy in self.css_strategies:
           if strategy.cost > self.cost_threshold:
               break  # Don't try expensive strategies
           # ... try strategy ...
   ```

3. **Optimize cache invalidation**
   - Invalidate when page navigates
   - Invalidate after actions that change DOM
   - Use LRU cache for memory management

4. **Performance testing**
   - Baseline measurement (before optimization)
   - After each optimization: measure improvement
   - Verify no regressions

5. **Memory optimization**
   - Use generators instead of lists where possible
   - Limit selector cache size
   - Clean up temporary objects

#### Performance Targets

| Metric | Baseline | Target | Optimized |
|--------|----------|--------|-----------|
| Scan 100 elements | - | <5s | <3s |
| Strategy generation | - | <10ms/elem | <5ms/elem |
| Validation | - | <10ms/selector | <5ms/selector |
| Memory (1000 elems) | - | <50MB | <30MB |
| Success rate | 85% | >90% | >95% |

#### Deliverables

- [ ] Cache implementation completed
- [ ] Batch validation implemented
- [ ] Performance metrics documented
- [ ] Memory usage optimized
- [ ] Speed improvements measured

#### Acceptance Criteria

- Performance within targets
- No memory leaks
- Success rate improved
- No functional regressions

#### Risks & Mitigation

- **Risk**: Over-caching causes stale data
  - **Mitigation**: Define clear invalidation rules
  - **Mitigation**: Add cache size limits

- **Risk**: Premature optimization adds complexity
  - **Mitigation**: Profile first, optimize hot paths only
  - **Mitigation**: Keep non-optimized code for comparison

#### Time Estimate

- **Development**: 6 hours
- **Testing/Profiling**: 4 hours
- **Documentation**: 2 hours
- **Total**: 12 hours

### Day 4: Real-World Optimization

#### Tasks

1. **Run optimized code on real websites**
   - Same websites from Phase 3
   - Compare metrics (before/after optimization):
     - Success rate
     - Average cost
     - Scan time
     - Memory usage

2. **A/B testing framework**
   ```python
   def compare_locators_v1_vs_v2(page):
       # Run old scanner
       old_elements = await old_scanner.scan(page)

       # Run new scanner
       new_elements = await new_scanner.scan(page)

       # Compare metrics
       return {
           'old_success_rate': calculate_success(old_elements),
           'new_success_rate': calculate_success(new_elements),
           'old_avg_cost': avg_cost(old_elements),
           'new_avg_cost': avg_cost(new_elements),
           'old_time': old_time,
           'new_time': new_time,
       }
   ```

3. **Tune strategy priorities based on data**
   - If certain strategies rarely succeed, lower priority
   - If certain strategies always succeed on specific sites, prioritize
   - Create site-specific profiles (optional)

4. **Optimize for common cases**
   - Fast path for elements with IDs
   - Fast path for input elements with name attributes
   - Cache common XPath patterns

5. **Document performance gains**
   - Create performance report
   - Document optimization techniques
   - Share learnings

#### Before/After Comparison

Expected improvements:

| Metric | Before Optimization | After Optimization | Improvement |
|--------|---------------------|-------------------|-------------|
| GitHub.com unique rate | 85% | 92% | +8% |
| Scan time (100 elems) | 5200ms | 2800ms | 46% faster |
| Memory usage | 45MB | 28MB | 38% less |
| Avg cost | 0.28 | 0.22 | 21% better |

#### Deliverables

- [ ] A/B test results showing improvements
- [ ] Performance comparison report
- [ ] Strategy priority tuning based on data
- [ ] Common-case optimizations

#### Acceptance Criteria

- >90% success rate on all tested sites
- Performance within targets
- Clear performance improvements documented
- Optimizations don't reduce success rate

#### Time Estimate

- **Testing**: 5 hours
- **Optimization**: 4 hours
- **Analysis**: 3 hours
- **Total**: 12 hours

### Day 5: Production Readiness

#### Tasks

1. **Security review**
   - Check for XSS in selector generation
   - Verify proper escaping
   - Review file I/O (no unsafe operations)

2. **Error handling review**
   - Verify all exceptions caught
   - Check error messages don't leak sensitive data
   - Ensure graceful degradation

3. **Documentation finalization**
   - Update all docstrings
   - Update README.md
   - Update CHANGELOG.md
   - Create user-facing documentation

4. **Create migration guide**
   ```markdown
   # Migrating to New Element Locator System

   ## Changes
   - Elements now have `best_css_selector` and `best_xpath` fields
   - `element.get_locator()` method for retrieving optimal locator
   - `element.locator_cost` indicates selector quality
   - `element.locator_strategy` shows which strategy was used

   ## Backward Compatibility
   - Old `element.selector` field still works (populated with best CSS)
   - `element.xpath` field still works (populated with best XPath)
   - No breaking changes to existing API

   ## New Features
   - Much higher success rate for element identification
   - Better selectors (more unique, more stable)
   - Fallback options when primary locator fails
   - Detailed metrics on locator quality

   ## Benefits
   - `highlight` command works more reliably
   - Fewer "strict mode violation" errors
   - More robust test scripts
   ```

5. **Final code review**
   - Review all changes
   - Ensure code quality standards
   - Check for dead code
   - Verify documentation completeness

6. **Create release notes**
   - List all new features
   - Document improvements
   - Note any known limitations

7. **Tag/commit final version**
   ```bash
   git tag -a v2.0.0 -m "Release element location strategy v2.0.0"
   git push origin v2.0.0
   ```

#### Production Readiness Checklist

- [ ] All tests passing
- [ ] Code coverage >= 90%
- [ ] Performance within targets
- [ ] No known critical bugs
- [ ] Security review completed
- [ ] Documentation complete
- [ ] Migration guide written
- [ ] Release notes prepared
- [ ] Code reviewed
- [ ] Tagged for release

#### Deliverables

- [ ] Production-ready codebase
- [ ] Complete documentation
- [ ] Release notes
- [ ] Migration guide
- [ ] Security review passed

#### Acceptance Criteria

- All production readiness criteria met
- Feature complete and tested
- Ready for user testing

#### Time Estimate

- **Review & Security**: 4 hours
- **Documentation**: 4 hours
- **Final checks**: 2 hours
- **Total**: 10 hours

### Phase 4 Summary

**Total Hours**: 10 + 12 + 12 + 12 + 10 = **56 hours** (~7 working days)

**Key Deliverables**:
- 90%+ test coverage
- Performance optimized
- Edge cases handled
- Production-ready code
- Complete documentation

**Phase 4 Complete When**: Code is production-ready with comprehensive tests and documentation

---

## Risk Management

### Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| **Performance issues** | Medium | High | **High** | Aggressive caching, batch operations, early optimization |
| **Browser compatibility** | Low | High | **Medium** | Test on multiple browsers, use widely-supported selectors |
| **Complex pages break strategies** | Medium | Medium | **Medium** | Extensive real-world testing, fallback mechanisms |
| **Schedule overrun** | Medium | Medium | **Medium** | Buffer time in estimate, defer non-critical features |
| **Test coverage too low** | Low | Medium | **Low** | Dedicated testing phase, CI enforcement |
| **XPath performance issues** | Low | High | **Medium** | CSS first, limit XPath usage, optimize XPath expressions |
| **Dynamic content breaks validation** | Medium | High | **High** | Accept eventual consistency, document limitations |
| **Team member unavailability** | Low | Medium | **Low** | Knowledge sharing, code reviews, documentation |

### Mitigation Strategies

#### High-Risk Items

1. **Performance Issues**
   - **Proactive**: Design with caching from Day 1
   - **Monitoring**: Measure performance daily
   - **Contingency**: If performance target not met by Day 3 of Phase 4, reduce validation strictness

2. **Dynamic Content Breaks Validation**
   - **Proactive**: Document that selectors are validated at scan time
   - **Design**: Provide warning when element not found (not hard error)
   - **User Education**: Document best practices (rescan after changes)

#### Medium-Risk Items

3. **Browser Compatibility**
   - **Proactive**: Test on Chrome, Firefox, Safari during Phase 3
   - **Mitigation**: Use Playwright's abstraction layer
   - **Fallback**: Provide browser-specific workarounds (if needed)

4. **Schedule Overrun**
   - **Buffer**: 10% buffer in all estimates
   - **Deferral**: Defer edge cases to Phase 4 (or future)
   - **Priority**: Focus on P0/P1 items first

### Monitoring & Tracking

**Weekly Risk Review**:
- Every Friday, assess risks
- Update risk matrix
- Decide on mitigations needed

**Escalation Path**:
- If high risk becomes imminent → Daily standup discussion
- If multiple risks materialize → Emergency planning session
- If schedule slips >2 days → Re-plan remaining phases

---

## Success Metrics

### Phase-Level KPIs

| Phase | Success Criteria | Measurement |
|-------|------------------|-------------|
| **Phase 1** | Core algorithm working | 100% unit tests pass |
| **Phase 1** | Cost model accurate | Cost ordering matches expected |
| **Phase 2** | 12 CSS strategies work | >90% success on test elements |
| **Phase 2** | Type-specific strategies work | Different types use different orders |
| **Phase 3** | XPath integration works | 5 XPath strategies implemented |
| **Phase 3** | End-to-end pipeline works | Real website tests pass |
| **Phase 4** | Test coverage achieved | Coverage > 90% |
| **Phase 4** | Performance targets met | Speed & memory within targets |
| **Phase 4** | Production ready | All checklists complete |

### Final Success Criteria

**Must Have** (Critical):
- ✅ 90%+ test coverage
- ✅ 95%+ success rate on real websites
- ✅ No critical bugs
- ✅ Performance within targets
- ✅ All P0 & P1 strategies implemented

**Should Have** (Important):
- ✅ 95%+ test coverage
- ✅ 85%+ elements use CSS (not XPath)
- ✅ Average cost < 0.25
- ✅ Edge cases handled gracefully
- ✅ Complete documentation

**Nice to Have** (Optional):
- ✅ 100% test coverage
- ✅ 98%+ success rate
- ✅ Average cost < 0.20
- ✅ Site-specific optimizations
- ✅ Visual debugging tools

### Tracking & Reporting

**Weekly Progress Report**:
- Phase completion status
- Hours spent vs. estimated
- Tests passing vs. total
- Code coverage
- Known issues/risks

**Phase Completion Report**:
- What was completed
- What was deferred
- Key learnings
- Next phase plan
- Any changes to overall plan

---

## Rollout Plan

### Development Phases

**Week 1**: Foundation (Core algorithm, cost model, validation)
**Week 2**: CSS Strategies (12 strategies, type-specific optimization)
**Week 3**: XPath & Integration (5 XPath strategies, end-to-end)
**Week 4**: Testing & Optimization (90%+ coverage, performance, polish)

**Total Duration**: 3-4 weeks

### Pre-Production Checklist

Before deploying to production:

- [ ] All phases complete
- [ ] All success metrics met
- [ ] Final code review completed
- [ ] Security review passed
- [ ] Performance tested
- [ ] Documentation complete
- [ ] Migration guide prepared
- [ ] Rollback plan ready (if needed)

### Staged Rollout

**Stage 1: Internal Testing (1 week)**
- Deploy to development environment
- Internal team testing
- Collect feedback
- Fix critical issues

**Stage 2: Beta Users (1 week)**
- Opt-in beta for volunteer users
- Monitor usage patterns
- Collect success metrics
- Address user feedback

**Stage 3: Full Release**
- Announce to all users
- Monitor support requests
- Track key metrics
- Prepare quick-fix patches if needed

### Rollback Plan

If critical issues found:

1. **Immediate**: Fix forward (if quick fix available)
2. **Within 1 day**: Hotfix release
3. **If unfixable**: Revert to previous version
   - Keep branch for V2.1
   - Communicate timeline for re-release

### Post-Release Monitoring

**Metrics to Track**:

- **Success Metrics**:
  - Element identification success rate
  - Average locator cost
  - CSS vs XPath ratio
  - User-reported issues

- **Performance Metrics**:
  - Scan time
  - Memory usage
  - Cache hit rate

- **Usage Metrics**:
  - Number of scans per user
  - Most common element types
  - Most common strategies used

**Review After 1 Week**:
- Analyze all metrics
- Identify remaining issues
- Plan V2.1 improvements

---

## Appendix

### A. Detailed Time Estimate

| Phase | Days | Hours | Notes |
|-------|------|-------|-------|
| Phase 1: Foundation | 5 | 49 | Core framework |
| Phase 2: CSS Strategies | 5 | 50 | 12 strategies |
| Phase 3: XPath & Integration | 5 | 57 | 5 XPath + integration |
| Phase 4: Testing & Optimization | 5 | 56 | 90% + performance |
| **Total** | **20** | **212** | **~3-4 weeks** |

**Buffer**: Add 10-15% buffer for risks (23 days ~ 4 weeks)

### B. Staffing Estimate

**One Developer**:
- Can complete all phases
- Focused knowledge
- Consistent implementation

**Two Developers**:
- Phase 1: Pair programming (foundation)
- Phase 2: Split strategies (Developer A: P0/P1, Developer B: P2)
- Phase 3: Pair on integration
- Phase 4: Split testing/optimization

### C. Dependencies

**External Dependencies**:
- Playwright: Already available
- Python 3.8+: Already available
- pytest: Already available

**Internal Dependencies**:
- Existing Element class (needs modification)
- Existing Scanner class (needs modification)
- Existing Highlighter class (needs modification)

### D. Assumptions

**Assumptions Made**:
1. Developer has 6-8 productive hours per day
2. No major external disruptions
3. Access to test websites for real-world testing
4. Existing test infrastructure adequate
5. No major refactoring of unrelated code needed
6. Management supports time needed for testing

**If Assumptions Wrong**:
- Adjust timeline by corresponding factor
- Negotiate scope reduction
- Defer edge cases to future release

---

**Plan End**
