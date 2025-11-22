# Changelog - Selector CLI

All notable changes to Selector CLI will be documented in this file.

## [Phase 4 Complete - Final] - 2025-11-23

### Added - Variable Expansion
- **Variable Expansion**:
  - `$var` - Simple variable reference
  - `${var}` - Variable with explicit boundary
  - Automatic expansion in all commands
  - Error handling for undefined variables
- **VariableExpander** utility class
- **Integration**: Variables expand before command parsing in REPL

### Usage Examples
```bash
# Set variables
set base_url = https://example.com
set api_path = /api/v1
set timeout = 30

# Use variables - simple reference
open $base_url

# Use variables - with boundary
open ${base_url}/login
export json > ${api_path}/data.json

# Mixed usage
open $base_url${api_path}/users
```

### Technical Details
**New Components**:
- `src/core/variable_expander.py` - VariableExpander class

**Modified Files**:
- `src/repl/main.py` - Integrated variable expansion before parsing

**Tests**:
- `tests/test_variable_expansion.py` - 7 test suites (all passing)

**Lines Added**: ~200 lines

---

## [Phase 4 Extended Complete] - 2025-11-23

### Added - Macro System and Script Execution
- **Macro System**:
  - `macro <name> <command>` - Define a macro
  - `run <name>` - Execute a macro
  - `macros` - List all defined macros
- **Script Execution**:
  - `exec <filepath>` - Execute script file (.sel format)
  - Support for comments (#) and empty lines
  - Line-by-line execution with error reporting
- **XPath Generation**:
  - Automatic XPath calculation during scan
  - ID-based XPath when available
  - Path-based XPath as fallback

### Usage Examples
```bash
# Define and run macros
macro analyze_inputs add input
run analyze_inputs

# Complex macro
macro login_flow add input where type="email"
run login_flow

# Execute script file
exec analyze.sel

# Script file format (.sel):
# analyze.sel
open https://example.com
scan
add input
add button
list
```

### Technical Details
**New Components**:
- `src/core/macro.py` - MacroManager class
- `PHASE4_EXTENDED_GRAMMAR.md` - Complete grammar specification

**Modified Files**:
- `src/parser/lexer.py` - Added MACRO/RUN/MACROS/EXEC tokens, LBRACE/RBRACE
- `src/parser/parser.py` - Added macro and exec command parsing
- `src/commands/executor.py` - Added macro and script execution
- `src/core/context.py` - Added MacroManager integration
- `src/core/scanner.py` - Added XPath generation

**Tests**:
- `tests/test_macro_script.py` - 5 test suites (all passing)
- `tests/test_xpath.py` - XPath generation tests

**Lines Added**: ~450 lines

---

## [Phase 4 Complete] - 2025-11-23

### Added - Persistence and Variables
- **Collection Persistence**:
  - `save <name>` - Save current collection to file
  - `load <name>` - Load collection from file
  - `saved` - List all saved collections
  - `delete <name>` - Delete saved collection
- **Variable System**:
  - `set <name> = <value>` - Set a variable
  - `vars` - List all variables
- **Storage Manager**:
  - JSON-based storage in `~/.selector-cli/collections/`
  - Automatic filename sanitization
  - Metadata preservation (URL, timestamp, count)

### Usage Examples
```bash
# Save and load collections
add input where type="email"
save login_form
load login_form

# List and manage saved collections
saved
delete old_collection

# Variables
set timeout = 30
set base_url = "https://example.com"
vars
```

### Technical Details
**New Components**:
- `src/core/storage.py` - StorageManager class

**Modified Files**:
- `src/parser/lexer.py` - Added SAVE/LOAD/SAVED/DELETE/SET/VARS tokens
- `src/parser/parser.py` - Added persistence command parsing
- `src/commands/executor.py` - Added persistence command execution

**Tests**:
- `tests/test_phase4_persistence.py` - 5 test suites (all passing)

**Lines Added**: ~500 lines

---

## [Phase 3 Core Complete] - 2025-11-23

### Added - Code Generation and Export
- **Export command**: `export <format> [> filename]`
- **3 Code Generators**:
  - Playwright (Python) - Generate Playwright automation code
  - Selenium (Python) - Generate Selenium automation code
  - Puppeteer (JavaScript) - Generate Puppeteer automation code
- **3 Data Exporters**:
  - JSON - Export elements as JSON
  - CSV - Export elements as CSV
  - YAML - Export elements as YAML
- **File redirection**: `export playwright > test.py`
- **Automatic variable naming**: Intelligent variable name generation from element properties

### Usage Examples
```bash
# Print generated code to console
export playwright
export selenium
export puppeteer

# Export data formats
export json
export csv
export yaml

# Write to file
export playwright > login_test.py
export json > elements.json
export csv > data.csv
```

### Implementation Details
- Generators architecture with base class and concrete implementations
- Smart selector formatting (prefers CSS selectors, falls back to generated)
- Python-friendly variable name sanitization
- UTF-8 file writing with error handling

### Tests
- ✅ 8 test suites (all passing)
- ✅ Export command parsing (8 cases)
- ✅ All 6 generators tested
- ✅ File export functionality tested
- ✅ Backward compatibility maintained

### Technical Details
**New Components**:
- `src/generators/base.py` - CodeGenerator base class
- `src/generators/playwright_gen.py` - Playwright generator
- `src/generators/selenium_gen.py` - Selenium generator
- `src/generators/puppeteer_gen.py` - Puppeteer generator
- `src/generators/data_exporters.py` - JSON/CSV/YAML exporters

**Modified Files**:
- `src/parser/lexer.py` - Added EXPORT and format tokens
- `src/parser/parser.py` - Added export command parsing
- `src/commands/executor.py` - Added export execution

**Lines Added**: +896 lines

---

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
