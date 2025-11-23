# Selector CLI - Interactive Web Element Selection Tool

Interactive command-line tool for web element selection and manipulation.

## Features

- Interactive REPL with contextual prompt
- Browser control (open URLs)
- Element scanning
- Collection management (add, remove, clear)
- Simple WHERE clause filtering (=, !=)
- Element querying (list, show, count)
- **Visual feedback** - Highlight elements in browser (Phase 5)
- **Set operations** - Union, intersect, difference for collections (Phase 5)
- **Command history** - History viewing and command replay (Phase 5)
- **Tab completion** - Auto-complete commands, element types, field names, and more (Phase 5)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**Note for Windows users**: Tab completion will be automatically enabled via `pyreadline3`. If you see "Warning: readline not available", run:
```bash
pip install pyreadline3
```

## Usage

```bash
python selector-cli.py
```

## Commands

### Browser Commands
```
open <url>              Open a URL
```

### Scan Commands
```
scan                    Scan page for elements
```

### Collection Commands
```
add <target>            Add elements to collection
add <target> where <condition>
remove <target>         Remove elements from collection
clear                   Clear collection
```

### Query Commands
```
list                    List collection
list <target>           List specific elements
show                    Show collection details
show <target>           Show element details
count                   Count collection elements
```

### Visual Feedback (Phase 5)
```
highlight               Highlight current collection
highlight <target>      Highlight specific elements
highlight <target> where <condition>
unhighlight             Remove all highlights
```

### Set Operations (Phase 5)
```
union <collection>      Combine with saved collection
intersect <collection>  Keep only common elements
difference <collection> Remove elements in other collection
unique                  Remove duplicates
```

### Command History (Phase 5)
```
history                 Show all commands
history <n>             Show last n commands
!n                      Execute command at index n
!!                      Execute last command
```

### Tab Completion (Phase 5)
Press **Tab** at any time to auto-complete:
- **Commands**: `ad<TAB>` → `add`, `hi<TAB>` → `highlight`
- **Element types**: `add in<TAB>` → `add input`
- **Field names**: `where ty<TAB>` → `where type`
- **Operators**: `type con<TAB>` → `type contains`
- **Export formats**: `export pla<TAB>` → `export playwright`
- **Collection names**: `union te<TAB>` → shows saved collections starting with "te"
- **File paths**: `exec my<TAB>` → completes file paths

Tab completion is context-aware and suggests relevant options based on what you've already typed.

### Targets
```
input, button, select, textarea, a
[5]                     Single index
[1,2,3]                 Multiple indices
all                     All elements
```

### WHERE Conditions (Phase 1)
```
where type="email"
where id="submit-btn"
where name!="hidden"
```

### Utility
```
help                    Show help
quit, exit, q          Exit CLI
```

## Example Session

```bash
selector> open https://example.com/login
Opened: https://example.com/login

selector(example.com)> scan
Scanned 15 elements

selector(example.com)> add input where type="email"
Added 1 element(s) to collection. Total: 1

selector(example.com)[1]> add input where type="password"
Added 1 element(s) to collection. Total: 2

selector(example.com)[2]> add button where type="submit"
Added 1 element(s) to collection. Total: 3

selector(example.com)[3]> list
Elements (3):
  [0] input type="email" placeholder="Email"
  [1] input type="password" placeholder="Password"
  [2] button type="submit" text="Sign In"

selector(example.com)[3]> show [0]

[0] input
  Selector: input[type="email"]
  Type: email
  Placeholder: Email

selector(example.com)[3]> count
Collection contains 3 element(s)

selector(example.com)[3]> quit
Shutting down...
Goodbye!
```

## Project Structure

```
selector-cli/
├── selector-cli.py         # Entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── src/
│   ├── repl/
│   │   └── main.py        # REPL main loop
│   ├── parser/
│   │   ├── lexer.py       # Tokenization
│   │   ├── parser.py      # Syntax analysis
│   │   └── command.py     # Command data structures
│   ├── commands/
│   │   └── executor.py    # Command execution
│   └── core/
│       ├── element.py     # Element class
│       ├── collection.py  # ElementCollection
│       ├── browser.py     # BrowserManager
│       ├── scanner.py     # ElementScanner
│       └── context.py     # Execution context
├── tests/
└── examples/
```

## Design Documents

See the design documents for full specification:
- `../selector-explorer/selector-cli-design-v1.0.md` - Complete system design
- `../selector-explorer/selector-cli-grammar-v1.0.md` - EBNF grammar specification
- `../selector-explorer/selector-cli-index-v1.0.md` - Documentation index

## Phase 1 Status

**Implemented:**
- ✅ REPL with basic prompt
- ✅ Commands: open, scan, list, add, remove, show, count, clear
- ✅ Simple WHERE conditions (=, !=)
- ✅ Collection management
- ✅ Element scanning

**Phase 2 Coming Soon:**
- Complex WHERE clauses (and, or, not)
- String operators (contains, starts, ends, matches)
- Index ranges [1-10]
- keep, filter commands

## Version

Phase 1 MVP - 2025-11-22
