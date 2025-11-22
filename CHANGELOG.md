# Changelog - Selector CLI

All notable changes to Selector CLI will be documented in this file.

## [Unreleased] - 2025-11-23

### Changed
- **Auto-scan after open** - `open` command now automatically scans the page after loading
  - No need to manually run `scan` after opening a URL
  - Returns: "Opened: {url}\nAuto-scanned {N} elements"
  - User can still manually run `scan` to re-scan if needed

---

## [Phase 2 Complete] - 2025-11-23

### Added - Enhanced Filtering (Phase 2)
- **Complex WHERE clause support**
  - Logical operators: `and`, `or`, `not`
  - Parentheses for grouping: `(condition) and condition`
  - Operator precedence: Parentheses > NOT > AND > OR
- **Comparison operators** for numeric fields
  - Greater than: `>`
  - Greater than or equal: `>=`
  - Less than: `<`
  - Less than or equal: `<=`
- **String matching operators**
  - Contains: `text contains "Submit"`
  - Starts with: `id starts "user_"`
  - Ends with: `name ends "_input"`
  - Regex match: `text matches "[0-9]+"`
- **Range selection** for indices
  - Simple range: `[1-10]` expands to [1,2,3,4,5,6,7,8,9,10]
  - Mixed notation: `[1,3,5-8,10]`
- **Boolean field support**
  - Standalone fields: `where visible` (implies = true)
  - Explicit: `where disabled = false`

### Changed
- **Parser** - Implemented recursive descent parser with operator precedence
- **Executor** - Added condition tree evaluator with recursive evaluation
- **Backward compatibility** - Phase 1 simple conditions still work

### Tests
- ✅ Parser tests (22 test cases) - `test_phase2_parser.py`
- ✅ Integration tests (7 test suites) - `test_phase2_integration.py`
- ✅ Lexer tests - `test_phase2_lexer.py`
- ✅ Phase 1 compatibility tests - `test_mvp.py`

### Examples
```
# Complex conditions with AND/OR/NOT
add input where (type="text" or type="email") and not disabled

# Numeric comparisons
list where index > 5 and index < 20

# String matching
add button where text contains "Submit"
add input where id starts "user_"
add input where name ends "_input"

# Range selection
add [1-10]
add [1,3,5-8,10]

# Boolean fields
add input where visible
add button where not disabled
```

### Technical Details
**Files Modified**:
- `src/parser/lexer.py` - Added 14 new token types
- `src/parser/command.py` - Added ConditionNode tree structure
- `src/parser/parser.py` - Complete rewrite with recursive descent parser (395 lines)
- `src/commands/executor.py` - Added condition tree evaluator (381 lines)

**New Files**:
- `tests/test_phase2_parser.py` (219 lines)
- `tests/test_phase2_integration.py` (410 lines)
- `tests/test_phase2_lexer.py` (134 lines)

**Lines Added**: ~1,000 lines

---

## [Phase 2 WIP] - 2025-11-22 (Superseded by completion above)

### Added
- **Lexer enhancements** for Phase 2 features
  - Comparison operators: `>`, `>=`, `<`, `<=`
  - String operators: `contains`, `starts`, `ends`, `matches`
  - Parentheses: `(`, `)`
  - Dash for ranges: `-`
  - Boolean literals: `true`, `false`
- **Data structures** for complex conditions
  - `ConditionNode` class for condition trees
  - `ConditionType` enum (SIMPLE, COMPOUND, UNARY)
  - Extended `Operator` enum with all Phase 2 operators
  - `RANGE` target type for `[1-10]` syntax
- **Tests** for lexer enhancements (`test_phase2_lexer.py`) - all passing ✅
- **Documentation** - `PHASE2_CONTINUE.md` with complete implementation guide

### Status
- ✅ Lexer: Complete and tested
- ✅ Data structures: Complete
- ⏳ Parser: Design ready, implementation pending
- ⏳ Executor: Design ready, implementation pending
- ⏳ Integration: Pending

### Next Session
Continue from `PHASE2_CONTINUE.md` - implement parser and executor (est. 3-4 hours)

---

## [Phase 1 MVP] - 2025-11-22

### Added
- ✅ Interactive REPL with contextual prompt
- ✅ Browser control commands: `open`
- ✅ Element scanning: `scan`
- ✅ Collection management: `add`, `remove`, `clear`
- ✅ Query commands: `list`, `show`, `count`
- ✅ Simple WHERE clause filtering: `=`, `!=`
- ✅ Target types: element types, indices, multiple indices, all
- ✅ Help system: `help`
- ✅ Clean exit: `quit`, `exit`, `q`
- ✅ Complete test suite (unit + integration tests)
- ✅ Comprehensive documentation

### Changed
- **[2025-11-22 PM]** Fixed import errors - changed from relative to absolute imports
  - Updated 9 files to use `from src.` prefix
  - Entry point now properly initializes package
  - All tests passing after fix

- **[2025-11-22 PM]** Auto-clear on new page (User Request)
  - `open` command now clears `all_elements` and `collection`
  - Prevents stale elements from previous page
  - Added test: `tests/test_clear_on_open.py`
  - Prompt correctly reflects empty collection after opening new page

### Technical Details

**Project Structure**:
```
selector-cli/
├── selector-cli.py              # Entry point
├── src/
│   ├── repl/main.py            # REPL loop
│   ├── parser/                 # Lexer, Parser, Command structures
│   ├── commands/               # Command execution
│   └── core/                   # Element, Collection, Browser, Scanner, Context
├── tests/
│   ├── test_mvp.py            # Unit tests
│   ├── test_integration.py    # Integration tests
│   └── test_clear_on_open.py  # Auto-clear feature test
└── examples/
```

**Files Created**: 20 files
**Lines of Code**: ~1,600 lines
**Test Coverage**: Core functionality

### Fixed
- Import errors when running `python selector-cli.py`
- Stale elements remaining when opening new page

### Documentation
- `README.md` - User guide
- `QUICKSTART.md` - Quick start guide
- `IMPLEMENTATION.md` - Technical implementation details
- `IMPORT_FIX.md` - Import error fix documentation
- `AUTO_CLEAR_FEATURE.md` - Auto-clear feature documentation

### Tests
- ✅ Unit tests: Lexer, Parser, Command structures
- ✅ Integration test: Full workflow with local test page
- ✅ Feature test: Auto-clear on new page
- **All tests passing** ✅

## [Planned - Phase 2] - Future

### To Be Added
- Complex WHERE clauses: `and`, `or`, `not`, `()`
- String operators: `contains`, `starts`, `ends`, `matches`
- Comparison operators: `>`, `>=`, `<`, `<=`
- Index ranges: `[1-10]`
- Additional commands: `keep`, `filter`
- Enhanced error messages

## [Planned - Phase 3] - Future

### To Be Added
- Code generation: Export to Playwright, Selenium, Puppeteer
- Data export: JSON, CSV, YAML formats
- File redirection: `export playwright > test.py`

## [Planned - Phase 4] - Future

### To Be Added
- Collection persistence: `save`, `load`, `saved`, `delete`
- Variable system: `set`, `vars`
- Macros: `macro`, `run`
- Script execution: `exec`

## [Planned - Phase 5] - Future

### To Be Added
- Shadow DOM deep scanning: `scan --deep`
- Set operations: `union`, `intersect`, `difference`
- Command history: `history`, `!n`, `!!`
- Auto-completion for commands and fields

## [Planned - Phase 6] - Future

### To Be Added
- Comprehensive testing
- Full documentation and tutorials
- Performance optimization
- User guide with examples

---

## Version History

- **v0.1.0** (2025-11-22) - Phase 1 MVP Release
  - Initial implementation
  - Core REPL functionality
  - Basic commands and filtering
  - Auto-clear on new page feature
  - Complete test suite
