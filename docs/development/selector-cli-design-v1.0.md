# Selector CLI - Design Document v1.0

**Project Name**: Selector CLI
**Version**: 1.0
**Date**: 2025-11-22
**Status**: Design Phase

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Command Reference](#3-command-reference)
4. [Data Model](#4-data-model)
5. [Core Components](#5-core-components)
6. [User Interface](#6-user-interface)
7. [Implementation Plan](#7-implementation-plan)
8. [Technical Specifications](#8-technical-specifications)
9. [Use Cases](#9-use-cases)
10. [Appendix](#10-appendix)

---

## 1. Project Overview

### 1.1 Vision

**Selector CLI** is an interactive command-line tool that revolutionizes web element selection and manipulation. It combines the declarative power of SQL with the interactivity of a shell REPL, enabling developers to explore, filter, and export web element selectors with unprecedented ease.

### 1.2 Goals

**Primary Goals**:
- Provide an intuitive CLI for web element exploration
- Support complex filtering with SQL-like WHERE clauses
- Enable visual verification through element highlighting
- Generate production-ready selector code
- Save and reuse element collections

**Secondary Goals**:
- Support Shadow DOM and iframe traversal
- Enable macro/scripting capabilities
- Provide extensible command system
- Offer multiple export formats

### 1.3 Key Features

#### Core Features
- ✅ **Interactive REPL** - Immediate feedback, readline support
- ✅ **Rich Query Language** - SQL-like WHERE clauses
- ✅ **Collection Management** - Add, remove, filter elements
- ✅ **Visual Feedback** - Real-time element highlighting
- ✅ **Code Generation** - Export to Playwright, Selenium, etc.
- ✅ **Persistence** - Save and load collections

#### Advanced Features
- ✅ **Variables** - Store and reuse selections
- ✅ **Macros** - Record and replay command sequences
- ✅ **History** - Command history with search
- ✅ **Set Operations** - Union, intersection, difference
- ✅ **Deep Scanning** - Shadow DOM support

### 1.4 Target Users

- **QA Engineers** - Writing automated tests
- **Web Developers** - Debugging frontend issues
- **Scraping Engineers** - Building web scrapers
- **Automation Engineers** - Creating browser automation scripts
- **Students** - Learning web development and testing

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│                    (Terminal/Console)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     REPL Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Readline   │  │    Prompt    │  │   History    │      │
│  │   Support    │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Command Pipeline                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Lexer     │─▶│    Parser    │─▶│  Validator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Command Executor                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dispatcher │  │   Context    │  │    Error     │      │
│  │              │  │   Manager    │  │   Handler    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼──────────┐ ┌─▼───────────┐
│     Browser     │ │   Element    │ │  Collection │
│     Manager     │ │   Manager    │ │   Manager   │
│                 │ │              │ │             │
│ - Page Session  │ │ - Scanner    │ │ - Filter    │
│ - Navigation    │ │ - Indexer    │ │ - Set Ops   │
│ - State Track   │ │ - Highlighter│ │ - Storage   │
└─────────────────┘ └──────────────┘ └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Playwright API                            │
│              (Browser Automation Layer)                      │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

#### REPL Engine
- **Input Handling**: Read user commands
- **Line Editing**: Support readline features (history, completion)
- **Prompt Display**: Show contextual prompt
- **Output Formatting**: Pretty-print results

#### Command Pipeline
- **Lexer**: Tokenize command string
- **Parser**: Build command AST
- **Validator**: Check syntax and semantics

#### Command Executor
- **Dispatcher**: Route commands to handlers
- **Context Manager**: Maintain execution state
- **Error Handler**: Catch and display errors

#### Browser Manager
- **Session Management**: Control Playwright browser/page
- **Navigation**: Handle URL loading, refresh, back/forward
- **State Tracking**: Monitor page loading state

#### Element Manager
- **Scanner**: Discover elements on page
- **Indexer**: Assign unique indices to elements
- **Highlighter**: Visual element highlighting

#### Collection Manager
- **Storage**: Maintain current selection
- **Filtering**: Apply WHERE conditions
- **Set Operations**: Union, intersection, difference
- **Persistence**: Save/load collections

### 2.3 Data Flow

```
User Input ──▶ Lexer ──▶ Parser ──▶ Validator ──▶ Executor
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    │                 │                 │
                                    ▼                 ▼                 ▼
                            Browser Manager   Element Manager   Collection Manager
                                    │                 │                 │
                                    └─────────────────┼─────────────────┘
                                                      │
                                                      ▼
                                            Playwright API
                                                      │
                                                      ▼
                                               Browser/Page
```

---

## 3. Command Reference

### 3.1 Command Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **Browser** | open, refresh, wait, back, forward | Navigate and control browser |
| **Scan** | scan | Discover elements on page |
| **Collection** | add, remove, clear, keep, unique | Manage element collection |
| **Query** | list, show, count, stats, filter | Query elements |
| **Visual** | highlight, unhighlight, blink | Visual feedback |
| **Export** | export | Generate code/data |
| **Storage** | save, load, saved, delete | Persist collections |
| **Utility** | set, vars, macro, run, exec, history, help, exit | Utilities |

### 3.2 Command Syntax

Complete syntax is defined in **Grammar v1.0** (see `selector-cli-grammar-v1.0.md`).

#### Browser Commands
```bash
open <url>                  # Open URL
refresh                     # Reload page
wait <seconds>              # Wait specified seconds
back                        # Go back
forward                     # Go forward
```

#### Scan Commands
```bash
scan                        # Scan all elements
scan input                  # Scan only inputs
scan input, button          # Scan inputs and buttons
scan --deep                 # Deep scan (Shadow DOM)
scan --shadow               # Scan Shadow DOM
```

#### Collection Commands
```bash
# Add elements
add <target> [where <condition>]
add input                           # All inputs
add [1,2,3]                        # By index
add input where type="email"       # With condition

# Remove elements
remove <target> [where <condition>]
remove [1]
remove button where text="Cancel"

# Other operations
clear                      # Clear collection
keep where <condition>     # Keep matching elements
unique                     # Remove duplicates
```

#### Query Commands
```bash
list [target] [where <condition>]   # List elements
show [target]                       # Show details
count                               # Count elements
stats                               # Show statistics
filter where <condition>            # Filter (non-destructive)
```

#### Visual Commands
```bash
highlight [target] [options]        # Highlight elements
highlight                           # Highlight collection
highlight [1,2,3]                  # Highlight by index
highlight --label                   # With labels
highlight --color=red              # Custom color

unhighlight                         # Remove highlights
blink <target>                     # Blink effect
```

#### Export Commands
```bash
export <type> [> <file>]
export selectors               # CSS selectors
export playwright              # Playwright code
export selenium                # Selenium code
export json                    # JSON format
export csv                     # CSV format

export playwright > test.py    # To file
```

#### Storage Commands
```bash
save <name>                    # Save collection
load <name>                    # Load collection
saved                          # List saved collections
delete saved <name>            # Delete saved
import collection < <file>     # Import from file
```

#### Utility Commands
```bash
# Variables
set <var> = <target> [where <condition>]
vars                           # List variables

# Macros
macro <name> { <commands> }    # Define macro
run <name>                     # Run macro
exec <file>                    # Execute script

# History
history [n]                    # Show history
!!                             # Repeat last
!<n>                          # Repeat command n
history search <query>         # Search history

# Help
help [command]                 # Show help
exit | quit | q               # Exit CLI
```

### 3.3 WHERE Clause Syntax

#### Basic Conditions
```bash
where <field> <operator> <value>

where type = "email"
where index > 5
where text != ""
```

#### Operators
```bash
Comparison:  =, !=, >, >=, <, <=
String:      contains, starts, ends, matches
```

#### Compound Conditions
```bash
where <condition> and <condition>
where <condition> or <condition>
where not (<condition>)
where (<condition>)

where type="email" and placeholder != ""
where text="Submit" or text="确定"
where not (disabled=true)
where (type="text" or type="email") and has id
```

#### Special Conditions
```bash
where has <field>              # Has attribute
where visible = true           # Visibility
where enabled = true           # Enabled state

where has id
where has placeholder
where visible=true
where enabled=true
```

#### Fields
```bash
type, text, placeholder, name, id, class, value
index, tag, visible, enabled, disabled
```

### 3.4 Index Specification
```bash
[n]                   # Single index: [5]
[n,m,...]            # Multiple: [1,2,5]
[n-m]                # Range: [1-10]
```

---

## 4. Data Model

### 4.1 Element

Represents a single web element.

```python
class Element:
    """Web element representation"""

    # Identification
    index: int                      # Global unique index
    uuid: str                       # UUID for tracking

    # Basic Properties
    tag: str                        # Tag name (input, button)
    type: str                       # Type attribute
    text: str                       # Text content
    value: str                      # Value attribute

    # Attributes
    attributes: Dict[str, str]      # All HTML attributes
    # {
    #     'type': 'email',
    #     'placeholder': 'Email',
    #     'name': 'email',
    #     'id': 'email-input',
    #     'class': 'form-control'
    # }

    # Computed Properties
    name: str                       # name attribute
    id: str                         # id attribute
    classes: List[str]              # class list
    placeholder: str                # placeholder

    # Location
    selector: str                   # CSS selector
    xpath: str                      # XPath
    path: str                       # DOM path

    # State
    visible: bool                   # Visibility
    enabled: bool                   # Enabled state
    disabled: bool                  # Disabled state

    # Shadow DOM
    in_shadow: bool                 # In Shadow DOM?
    shadow_host: Optional[str]      # Host selector
    shadow_path: Optional[str]      # Path within shadow

    # Playwright
    locator: Locator               # Playwright Locator
    handle: ElementHandle          # Element handle

    # Metadata
    scanned_at: datetime           # When scanned
    page_url: str                  # Page URL
```

### 4.2 ElementCollection

Collection of elements with filtering and set operations.

```python
class ElementCollection:
    """Collection of elements"""

    # Storage
    elements: List[Element]
    _index: Dict[int, Element]     # Fast lookup by index

    # Metadata
    name: Optional[str]            # Collection name
    created_at: datetime
    modified_at: datetime

    # Methods
    def add(self, element: Element) -> None
    def remove(self, element: Element) -> None
    def clear(self) -> None

    def filter(self, condition: Condition) -> ElementCollection
    def contains(self, element: Element) -> bool
    def get(self, index: int) -> Optional[Element]

    def count(self) -> int
    def is_empty(self) -> bool

    # Set Operations
    def union(self, other: ElementCollection) -> ElementCollection
    def intersection(self, other: ElementCollection) -> ElementCollection
    def difference(self, other: ElementCollection) -> ElementCollection

    # Serialization
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> ElementCollection
```

### 4.3 Command

Parsed command representation.

```python
class Command:
    """Parsed command"""

    # Command components
    verb: str                      # add, remove, show, etc.
    target: Optional[Target]       # What to operate on
    condition: Optional[Condition] # WHERE clause
    options: Dict[str, Any]        # Command options

    # Metadata
    raw: str                       # Original string
    tokens: List[Token]            # Token list

    # Methods
    def validate(self) -> bool
    def __str__(self) -> str
```

### 4.4 Target

Specifies what elements to operate on.

```python
class Target:
    """Command target"""

    type: TargetType              # Type of target
    # TargetType: ELEMENT_TYPE | INDEX | RANGE | ALL | VARIABLE

    # Type-specific data
    element_type: Optional[str]   # input, button, etc.
    indices: Optional[List[int]]  # [1,2,3]
    range_start: Optional[int]    # Range start
    range_end: Optional[int]      # Range end
    variable: Optional[str]       # Variable name
```

### 4.5 Condition

WHERE clause condition tree.

```python
class Condition:
    """Condition expression"""

    type: ConditionType
    # ConditionType: SIMPLE | COMPOUND | UNARY

    # Simple condition
    field: Optional[str]          # type, text, etc.
    operator: Optional[Operator]  # =, !=, contains, etc.
    value: Optional[Any]          # Comparison value

    # Compound condition
    logic: Optional[LogicOp]      # AND, OR
    left: Optional[Condition]     # Left operand
    right: Optional[Condition]    # Right operand

    # Unary condition
    operand: Optional[Condition]  # For NOT

    # Methods
    def evaluate(self, element: Element) -> bool
    def __str__(self) -> str
```

### 4.6 Context

Execution context/state.

```python
class Context:
    """Execution context"""

    # Browser state
    browser: Optional[Browser]
    page: Optional[Page]
    current_url: Optional[str]

    # Elements
    all_elements: List[Element]        # All scanned elements
    collection: ElementCollection      # Current collection

    # Variables
    variables: Dict[str, Any]          # User variables

    # Macros
    macros: Dict[str, Macro]           # Defined macros

    # History
    history: List[str]                 # Command history

    # State
    last_scan_time: Optional[datetime]
    is_page_loaded: bool
```

---

## 5. Core Components

### 5.1 REPL Engine

```python
class SelectorREPL:
    """Interactive REPL"""

    def __init__(self):
        self.parser = CommandParser()
        self.executor = CommandExecutor()
        self.context = Context()
        self.prompt = PromptManager()
        self.history_manager = HistoryManager()

    async def run(self):
        """Main REPL loop"""
        self.initialize()

        while True:
            try:
                # Display prompt
                prompt_str = self.prompt.get_prompt(self.context)

                # Read input
                line = input(prompt_str)

                # Skip empty lines
                if not line.strip():
                    continue

                # Add to history
                self.history_manager.add(line)

                # Parse command
                command = self.parser.parse(line)

                # Execute
                result = await self.executor.execute(command, self.context)

                # Display result
                self.display_result(result)

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInterrupted")
                continue
            except Exception as e:
                self.display_error(e)
```

### 5.2 Command Parser

```python
class CommandParser:
    """Parse command strings"""

    def __init__(self):
        self.lexer = Lexer()
        self.grammar = Grammar()

    def parse(self, command_str: str) -> Command:
        """Parse command string into Command object"""

        # Tokenize
        tokens = self.lexer.tokenize(command_str)

        # Parse tokens
        ast = self.grammar.parse(tokens)

        # Build command
        command = self.build_command(ast)

        # Validate
        self.validate(command)

        return command

    def build_command(self, ast: AST) -> Command:
        """Build Command from AST"""
        ...

    def validate(self, command: Command) -> None:
        """Validate command semantics"""
        ...
```

### 5.3 Lexer

```python
class Lexer:
    """Tokenize command strings"""

    # Token types
    KEYWORDS = {
        'open', 'scan', 'add', 'remove', 'show', ...
    }

    OPERATORS = {
        '=', '!=', '>', '>=', '<', '<=',
        'contains', 'starts', 'ends', 'matches'
    }

    def tokenize(self, text: str) -> List[Token]:
        """Convert string to tokens"""
        tokens = []
        position = 0

        while position < len(text):
            # Skip whitespace
            if text[position].isspace():
                position += 1
                continue

            # Identifier or keyword
            if text[position].isalpha():
                token = self.read_identifier(text, position)
                tokens.append(token)
                position += len(token.value)
                continue

            # Number
            if text[position].isdigit():
                token = self.read_number(text, position)
                tokens.append(token)
                position += len(token.value)
                continue

            # String
            if text[position] in '"\'':
                token = self.read_string(text, position)
                tokens.append(token)
                position += len(token.value) + 2  # quotes
                continue

            # Operators and delimiters
            token = self.read_operator(text, position)
            if token:
                tokens.append(token)
                position += len(token.value)
            else:
                raise LexerError(f"Unexpected character: {text[position]}")

        return tokens
```

### 5.4 Command Executor

```python
class CommandExecutor:
    """Execute commands"""

    def __init__(self):
        # Register command handlers
        self.handlers = {
            'open': OpenCommandHandler(),
            'scan': ScanCommandHandler(),
            'add': AddCommandHandler(),
            'remove': RemoveCommandHandler(),
            'show': ShowCommandHandler(),
            'highlight': HighlightCommandHandler(),
            'export': ExportCommandHandler(),
            # ... more handlers
        }

    async def execute(self, command: Command, context: Context) -> Result:
        """Execute command"""

        # Get handler
        handler = self.handlers.get(command.verb)
        if not handler:
            raise UnknownCommandError(f"Unknown command: {command.verb}")

        # Execute
        try:
            result = await handler.execute(command, context)
            return result
        except Exception as e:
            raise CommandExecutionError(f"Error executing {command.verb}: {e}")
```

### 5.5 Condition Evaluator

```python
class ConditionEvaluator:
    """Evaluate WHERE conditions"""

    def evaluate(self, element: Element, condition: Condition) -> bool:
        """Check if element matches condition"""

        if condition.type == ConditionType.SIMPLE:
            return self.evaluate_simple(element, condition)

        elif condition.type == ConditionType.COMPOUND:
            left_result = self.evaluate(element, condition.left)
            right_result = self.evaluate(element, condition.right)

            if condition.logic == LogicOp.AND:
                return left_result and right_result
            elif condition.logic == LogicOp.OR:
                return left_result or right_result

        elif condition.type == ConditionType.UNARY:
            operand_result = self.evaluate(element, condition.operand)
            return not operand_result

        return False

    def evaluate_simple(self, element: Element, condition: Condition) -> bool:
        """Evaluate simple condition"""

        # Get field value
        field_value = self.get_field_value(element, condition.field)

        # Compare
        return self.compare(
            field_value,
            condition.operator,
            condition.value
        )

    def compare(self, left: Any, operator: Operator, right: Any) -> bool:
        """Compare values"""

        if operator == Operator.EQUALS:
            return left == right
        elif operator == Operator.NOT_EQUALS:
            return left != right
        elif operator == Operator.GREATER:
            return left > right
        elif operator == Operator.CONTAINS:
            return right in str(left)
        # ... more operators
```

### 5.6 Element Scanner

```python
class ElementScanner:
    """Scan page for elements"""

    async def scan(
        self,
        page: Page,
        element_types: List[str] = None,
        deep: bool = False
    ) -> List[Element]:
        """Scan page and return elements"""

        if element_types is None:
            element_types = ['input', 'button', 'a', 'select', 'textarea']

        elements = []
        index = 0

        for elem_type in element_types:
            # Query elements
            locators = await page.locator(elem_type).all()

            for locator in locators:
                # Build Element object
                element = await self.build_element(locator, index, elem_type)
                elements.append(element)
                index += 1

        # Deep scan for Shadow DOM
        if deep:
            shadow_elements = await self.scan_shadow_dom(page)
            for elem in shadow_elements:
                elem.index = index
                elements.append(elem)
                index += 1

        return elements
```

### 5.7 Highlighter

```python
class ElementHighlighter:
    """Highlight elements on page"""

    async def highlight(
        self,
        page: Page,
        elements: List[Element],
        options: HighlightOptions = None
    ) -> None:
        """Highlight elements"""

        for element in elements:
            await page.evaluate("""
                (selector, index, label) => {
                    const el = document.querySelector(selector);
                    if (!el) return;

                    // Add border
                    el.style.border = '3px solid red';
                    el.style.boxShadow = '0 0 10px rgba(255,0,0,0.6)';

                    // Add label if requested
                    if (label) {
                        const labelDiv = document.createElement('div');
                        labelDiv.textContent = `[${index}]`;
                        labelDiv.style.cssText = `
                            position: absolute;
                            background: red;
                            color: white;
                            padding: 4px 8px;
                            font-size: 12px;
                            z-index: 999999;
                        `;

                        const rect = el.getBoundingClientRect();
                        labelDiv.style.left = rect.left + 'px';
                        labelDiv.style.top = (rect.top - 25) + 'px';

                        document.body.appendChild(labelDiv);
                    }
                }
            """, element.selector, element.index, options.show_label if options else False)
```

---

## 6. User Interface

### 6.1 Prompt Design

```bash
# Default
selector>

# With active page
selector(example.com)>

# With collection
selector(example.com)[5]>

# With active variable context
selector(example.com)[5][$email-input]>

# Error state
selector(error)>
```

### 6.2 Output Formatting

#### Table Output
```
Index | Type     | Placeholder      | Selector
------|----------|------------------|-------------------------
[0]   | email    | Email address    | input[type="email"]
[1]   | password | Password         | input#password
[2]   | text     | Username         | input[name="username"]

Total: 3 elements
```

#### List Output
```
[0] input[type="email"]
    - placeholder: "Email address"
    - name: "email"
    - id: "email-input"
    - class: "form-control"

[1] input[type="password"]
    - placeholder: "Password"
    - name: "password"
    - id: "password-input"
```

#### Statistics Output
```
Page Statistics:
  Total Elements: 25

  By Type:
    input:    8
    button:   5
    a:       10
    select:   2

  In Collection: 5

  Shadow DOM:
    Found: 2 shadow hosts
    Elements in shadow: 12
```

### 6.3 Color Scheme

- **Success**: Green
- **Error**: Red
- **Warning**: Yellow
- **Info**: Blue
- **Highlight**: Cyan
- **Dimmed**: Gray

### 6.4 Auto-completion

Support tab completion for:
- Commands (add, remove, show, etc.)
- Element types (input, button, etc.)
- Fields (type, text, placeholder, etc.)
- Operators (=, !=, contains, etc.)
- Keywords (where, and, or, etc.)
- Saved collection names
- Variable names

---

## 7. Implementation Plan

### 7.1 Phase 1: MVP (Minimum Viable Product)

**Goal**: Basic interactive element selection

**Duration**: 2-3 weeks

**Features**:
- ✅ REPL with basic prompt
- ✅ Commands: open, scan, list, add, remove, show
- ✅ Simple WHERE conditions (=, !=)
- ✅ Basic highlighting
- ✅ Export selectors

**Deliverables**:
- Working REPL
- Basic command set
- Simple filtering
- Manual testing

### 7.2 Phase 2: Enhanced Filtering

**Goal**: Rich query capabilities

**Duration**: 2 weeks

**Features**:
- ✅ Complex WHERE clauses (and, or, not)
- ✅ String operators (contains, starts, ends, matches)
- ✅ Index ranges [1-10]
- ✅ keep, filter commands
- ✅ count, stats commands

**Deliverables**:
- Full WHERE clause support
- Comprehensive filtering
- Better output formatting

### 7.3 Phase 3: Code Generation

**Goal**: Production-ready exports

**Duration**: 1-2 weeks

**Features**:
- ✅ Export to Playwright
- ✅ Export to Selenium
- ✅ Export to Puppeteer
- ✅ Export to JSON/CSV/YAML
- ✅ File redirection

**Deliverables**:
- Multiple export formats
- Code templates
- Documentation

### 7.4 Phase 4: Persistence & Variables

**Goal**: Save and reuse work

**Duration**: 1-2 weeks

**Features**:
- ✅ save/load collections
- ✅ Variable system
- ✅ Macro definition and execution
- ✅ Script execution

**Deliverables**:
- Collection storage
- Variable/macro system
- Script files

### 7.5 Phase 5: Advanced Features

**Goal**: Power user features

**Duration**: 2-3 weeks

**Features**:
- ✅ Shadow DOM deep scanning
- ✅ Set operations (union, intersection, difference)
- ✅ History with search
- ✅ Auto-completion
- ✅ Better error messages

**Deliverables**:
- Shadow DOM support
- Advanced operations
- Enhanced UX

### 7.6 Phase 6: Polish & Documentation

**Goal**: Production ready

**Duration**: 1-2 weeks

**Features**:
- ✅ Comprehensive testing
- ✅ Full documentation
- ✅ Tutorial and examples
- ✅ Performance optimization

**Deliverables**:
- Test suite
- User guide
- API documentation
- Performance benchmarks

---

## 8. Technical Specifications

### 8.1 Technology Stack

- **Language**: Python 3.8+
- **Browser Automation**: Playwright
- **CLI Framework**: Custom REPL with readline
- **Parsing**: Hand-written recursive descent parser
- **Storage**: JSON files
- **Testing**: pytest

### 8.2 Dependencies

```
playwright>=1.40.0
prompt-toolkit>=3.0.0  # Advanced readline features
pygments>=2.0.0        # Syntax highlighting
click>=8.0.0           # CLI utilities
pyyaml>=6.0            # YAML support
```

### 8.3 Performance Requirements

- Command parsing: < 10ms
- Element scanning: < 2s for typical pages
- Highlighting: < 100ms per element
- Collection filtering: < 50ms for 1000 elements

### 8.4 Storage Format

Collections saved as JSON:

```json
{
  "name": "login-form",
  "created_at": "2025-11-22T10:30:00",
  "modified_at": "2025-11-22T10:35:00",
  "page_url": "https://example.com/login",
  "elements": [
    {
      "index": 0,
      "tag": "input",
      "type": "email",
      "selector": "input[type='email']",
      "attributes": {
        "type": "email",
        "placeholder": "Email",
        "name": "email"
      }
    }
  ]
}
```

---

## 9. Use Cases

### 9.1 Use Case 1: Analyze Login Form

**Actor**: QA Engineer

**Goal**: Extract selectors for login form automation

**Steps**:
```bash
selector> open https://example.com/login
selector> scan
selector> add input where type="email"
selector> add input where type="password"
selector> add button where text contains "Login"
selector> show
selector> export playwright > login_test.py
```

**Expected Output**:
```python
# login_test.py
email = page.locator('input[type="email"]')
password = page.locator('input[type="password"]')
login_btn = page.locator('button:has-text("Login")')
```

### 9.2 Use Case 2: Complex Form Analysis

**Actor**: Web Developer

**Goal**: Find all required fields

**Steps**:
```bash
selector> open https://example.com/signup
selector> scan
selector> add input where has required
selector> add select where has required
selector> list
selector> save required-fields
```

### 9.3 Use Case 3: Macro for Testing

**Actor**: Automation Engineer

**Goal**: Create reusable test setup

**Steps**:
```bash
selector> macro setup-login-test {
    open https://example.com/login
    scan
    add input where type="email"
    add input where type="password"
    add button where text="Login"
    save login-elements
}

selector> run setup-login-test
```

### 9.4 Use Case 4: Shadow DOM Debugging

**Actor**: Frontend Developer

**Goal**: Inspect Shadow DOM elements

**Steps**:
```bash
selector> open https://example.com/custom-components
selector> scan --deep
selector> list where in_shadow=true
selector> highlight
```

---

## 10. Appendix

### 10.1 Command Cheat Sheet

```
Browser:     open, refresh, wait, back, forward
Scan:        scan [types] [--deep] [--shadow]
Collection:  add, remove, clear, keep, unique
Query:       list, show, count, stats, filter
Visual:      highlight, unhighlight, blink
Export:      export [type] [> file]
Storage:     save, load, saved, delete saved
Utility:     set, vars, macro, run, exec, history, help, exit
```

### 10.2 Operator Reference

```
Comparison:  =, !=, >, >=, <, <=
String:      contains, starts, ends, matches
Logic:       and, or, not
Special:     has
```

### 10.3 Field Reference

```
type, text, placeholder, name, id, class, value
index, tag, visible, enabled, disabled
in_shadow, shadow_host
```

### 10.4 Export Formats

| Format | Description | File Extension |
|--------|-------------|----------------|
| selectors | CSS selectors only | .txt |
| playwright | Playwright Python code | .py |
| selenium | Selenium Python code | .py |
| puppeteer | Puppeteer JavaScript | .js |
| json | JSON data | .json |
| csv | CSV table | .csv |
| yaml | YAML data | .yaml |

### 10.5 Error Codes

| Code | Type | Description |
|------|------|-------------|
| E001 | Syntax Error | Invalid command syntax |
| E002 | Semantic Error | Invalid command semantics |
| E003 | Runtime Error | Error during execution |
| E004 | Network Error | Cannot access URL |
| E005 | Element Not Found | No matching elements |
| E006 | Storage Error | Cannot save/load |

### 10.6 Future Enhancements

- **iframe support**: Traverse into iframes
- **Multi-page**: Work with multiple pages/tabs
- **Recording**: Record user actions
- **AI assistant**: Natural language queries
- **VS Code extension**: GUI integration
- **Cloud sync**: Sync collections across devices
- **Collaboration**: Share collections with team

---

## Document Information

**Version**: 1.0
**Status**: Design Phase
**Last Updated**: 2025-11-22
**Authors**: Development Team
**Review Status**: Pending Review

---

## Changelog

**v1.0 (2025-11-22)**
- Initial design document
- Complete architecture definition
- Full command reference
- Data model specification
- Implementation plan
- Use cases and examples
