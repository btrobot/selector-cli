# Phase 3: XPath Enhancement & Integration - Task List

## Phase 3 Goals
- Enhance XPath strategies with proper escaping and position calculation
- Integrate with Scanner/Collection system
- Add debugging and logging
- Real browser testing preparation

## Task List

### ✅ Completed (from previous session)
- [x] Added XPath string escaping infrastructure
- [x] Updated XPath generator methods to use escaping
- [x] Created test file for XPath escaping

### 🔄 In Progress / Need Fixing
- [ ] Fix XPath string escaping logic (tests currently failing)
- [ ] Implement NTH_OF_TYPE position calculation
- [ ] Add debug logging to strategy engine

### 📋 To Do
- [ ] Add logging configuration
- [ ] Implement enhanced logging in strategy selection
- [ ] Prepare Scanner integration interface
- [ ] Create real browser test script
- [ ] Document XPath enhancements

---

## Priority Order

### High Priority (Required for Phase 3 completion)
1. Fix XPath string escaping
2. NTH_OF_TYPE position calculation
3. Debug logging infrastructure

### Medium Priority (Recommended)
4. Scanner integration interface
5. Enhanced error messages
6. Performance logging

### Low Priority (Optional)
7. Real browser test automation
8. Performance benchmarks
9. Phase 3 documentation

---

## Next Steps

### 1. Fix XPath String Escaping

Current issue: Escaping logic is too complex and tests are failing.

Simpler approach:
```python
def _escape_xpath_string(self, text: str) -> str:
    if not text:
        return "''"

    # No single quotes - use single quotes
    if "'" not in text:
        return f"'{text}'"

    # No double quotes - use double quotes
    if '"' not in text:
        return f'"{text}"'

    # Has both - split by single quotes and use concat
    parts = text.split("'")
    concat_parts = [f'"{part}"' for part in parts]
    return f"concat({', "\'", '.join(concat_parts)})"
```

### 2. NTH_OF_TYPE Position Calculation

Need to implement logic to find element's position among siblings of same tag.

Pseudo-code:
```python
def _generate_nth_of_type_selector(self, element: Element) -> Optional[str]:
    # Find all sibling elements with same tag
    # Count position of current element
    # Return selector with position
    pass
```

### 3. Debug Logging

Add logging to:
- Strategy selection process
- Validation attempts
- Success/failure of each strategy
- Final result selection

---

## Test Requirements

All tasks must include tests:
- Unit tests for each function
- Integration tests for combined functionality
- Logging verification tests

## Documentation

Update the following:
- Code comments for new functions
- Update PROGRESS_CHECK.md
- Update PHASE3_TASKS.md as tasks complete
