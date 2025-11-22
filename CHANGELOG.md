# Changelog - Selector CLI

All notable changes to Selector CLI will be documented in this file.

## [Phase 2 WIP] - 2025-11-22 (In Progress)

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
