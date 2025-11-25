# FIND Command - Supported Element Types

## Overview
The FIND command in Selector CLI v2.0 supports querying DOM elements by their tag name or special selectors.

## Supported Element Types

### Basic HTML5 Elements
1. **input** - Input fields (text, email, password, etc.)
   - Command: `find input`
   - Example: `find input where type="email"`

2. **button** - Button elements
   - Command: `find button`
   - Example: `find button where text contains "Submit"`

3. **select** - Dropdown/select elements
   - Command: `find select`
   - Example: `find select where visible`

4. **textarea** - Textarea elements
   - Command: `find textarea`
   - Example: `find textarea where placeholder contains "message"`

5. **div** - Div elements
   - Command: `find div`
   - Example: `find div where class contains "modal"`

### Links
6. **a** / **link** - Anchor/link elements (two aliases)
   - Short form: `find a`
   - Long form: `find link`
   - Example: `find a where href contains "/about"`
   - Example: `find link where visible and text contains "Login"`

### Special Selector
7. **all** / **\*** - All elements (wildcard)
   - Command: `find all`
   - Example: `find all where visible`
   - Note: Returns TargetType.ALL instead of a specific element type

## Usage Patterns

### Pattern 1: Basic Element Query
```
find <element_type>
```
Queries the DOM for all elements of the specified type and stores results in temp.

Examples:
- `find input` - Find all input fields
- `find button` - Find all buttons
- `find div` - Find all divs

### Pattern 2: With WHERE Clause
```
find <element_type> where <condition>
```
Filters elements during the DOM query.

Examples:
- `find button where visible`
- `find input where type="email"`
- `find div where class contains "modal"`
- `find a where text contains "Login"`

### Pattern 3: Complex Conditions (AND/OR)
```
find <element_type> where <condition> and|or <condition>
```
Combines multiple conditions with logical operators.

Examples:
- `find button where visible and enabled`
- `find input where type="email" or type="text"`
- `find a where visible and text contains "About"`

### Pattern 4: Refine Mode (.find)
```
.find where <condition>
```
Filters existing temp results without querying DOM.

Workflow example:
1. `find button` - Get all buttons → temp
2. `.find where visible` - Filter visible → new temp
3. `.find where text contains "Save"` - Filter further → final results

## Technical Details

### Token Mapping (Lexer)
Defined in `src/selector_cli/parser/lexer.py`:

```python
# Element types
'input': TokenType.INPUT
'button': TokenType.BUTTON
'select': TokenType.SELECT
'textarea': TokenType.TEXTAREA
'a': TokenType.LINK
'link': TokenType.LINK
'div': TokenType.DIV
'all': TokenType.ALL  # Mapped to TargetType.ALL
'*': TokenType.ALL    # Also supported
```

### Parser Behavior
In `src/selector_cli/parser/parser.py`:

- Element types → Target(type=TargetType.ELEMENT_TYPE, element_type="<type>")
- "all" / "*" → Target(type=TargetType.ALL, element_type=None)

### Executor Behavior
In `src/selector_cli/commands/executor.py`:

- Normal find (`find <type>`): Queries browser's `query_selector_all(<type>)`
- Refine find (`.find where...`): Filters `context.temp` directly
- "find all": Queries browser's `query_selector_all('*')`

## Examples Summary

| Pattern | Example Command | Description |
|---------|----------------|-------------|
| Basic | `find input` | All input fields |
| Attribute filter | `find input where type="email"` | Email inputs only |
| Contains filter | `find div where class contains "modal"` | Divs with 'modal' in class |
| Text filter | `find button where text contains "Login"` | Login button |
| AND logic | `find button where visible and enabled` | Visible AND enabled buttons |
| OR logic | `find input where type="email" or type="text"` | Email OR text inputs |
| Refine | `.find where visible` | Filter temp to visible only |
| All elements | `find all` or `find *` | All elements on page |

## Future Considerations

### Potentially Add More Element Types
Based on common HTML5 elements, these could be added:
- `span`, `p`, `h1`-`h6`, `ul`, `ol`, `li`
- `table`, `tr`, `td`, `th`
- `form`, `label`, `img`, `video`, `audio`
- `nav`, `header`, `footer`, `main`, `section`, `article`

### Type-List Support (Not Currently Implemented)
Could support queries like:
- `find button, input, a` - Find all buttons, inputs, and links
- `find [button, input, a]` - Alternative syntax

### Special Selectors (Not Currently Implemented)
Could support:
- `find * where visible` - All visible elements (already works as `find all`)
- `find where class contains "btn"` - Implicit "all" when no type specified

## Testing

All element types are tested in:
- `tests/test_v2_repl_fixes.py` - Basic parsing tests
- `demo_find_syntax.py` - Comprehensive demonstration
- `test_find_element_types.py` - Element type validation

Run tests with:
```bash
pytest tests/test_v2_repl_fixes.py -v
python demo_find_syntax.py
python test_find_element_types.py
```
