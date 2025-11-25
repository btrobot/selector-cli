"""
Demonstration of FIND command syntax - v2.0 features
"""
from selector_cli.parser.parser import Parser
from selector_cli.commands.executor import CommandExecutor
from selector_cli.core.context import Context
from selector_cli.core.element import Element


def demo_find_syntax():
    """Demonstrate all FIND command syntax variations"""

    print("=" * 70)
    print("SELECTOR CLI v2.0 - FIND COMMAND SYNTAX DEMONSTRATION")
    print("=" * 70)

    parser = Parser()
    context = Context(enable_history_file=False)
    executor = CommandExecutor()

    # Setup some sample elements for demonstration
    print("\n[Setting up demo elements...]")
    demo_elements = [
        Element(index=0, uuid='btn1', tag='button',
                attributes={'type': 'submit', 'class': 'primary'},
                visible=True, text='Login'),
        Element(index=1, uuid='btn2', tag='button',
                attributes={'type': 'button', 'class': 'secondary'},
                visible=True, text='Cancel'),
        Element(index=2, uuid='btn3', tag='button',
                attributes={'type': 'button', 'class': 'hidden'},
                visible=False, text='Hidden Delete'),
        Element(index=3, uuid='input1', tag='input',
                attributes={'type': 'email', 'placeholder': 'your@email.com'},
                visible=True),
        Element(index=4, uuid='input2', tag='input',
                attributes={'type': 'password', 'placeholder': 'Password'},
                visible=True),
        Element(index=5, uuid='div1', tag='div',
                attributes={'class': 'modal-dialog', 'role': 'dialog'},
                visible=True),
        Element(index=6, uuid='div2', tag='div',
                attributes={'class': 'modal-backdrop'},
                visible=False),
        Element(index=7, uuid='a1', tag='a',
                attributes={'href': '/about', 'class': 'nav-link'},
                visible=True, text='About'),
        Element(index=8, uuid='a2', tag='a',
                attributes={'href': '/contact', 'class': 'nav-link disabled'},
                visible=True, text='Contact'),
    ]

    context.candidates = demo_elements
    print(f"   Created {len(context.candidates)} demo elements")

    # Section 1: Basic FIND
    print("\n" + "=" * 70)
    print("SECTION 1: Basic FIND Commands")
    print("=" * 70)

    tests = [
        ("find button", "Find all buttons"),
        ("find input", "Find all input fields"),
        ("find div", "Find all div elements"),
        ("find a", "Find all anchor links"),
    ]

    for command_str, description in tests:
        print(f"\n[ {description} ]")
        print(f"   Command: {command_str}")
        try:
            cmd = parser.parse(command_str)
            print(f"   [OK] Parsed successfully")
            print(f"      - Verb: {cmd.verb}")
            print(f"      - Target: {cmd.target.element_type if cmd.target else 'None'}")
            print(f"      - Has condition: {cmd.condition_tree is not None}")
        except Exception as e:
            print(f"   [ERROR] {e}")

    # Section 2: FIND with WHERE conditions
    print("\n" + "=" * 70)
    print("SECTION 2: FIND with WHERE Conditions")
    print("=" * 70)

    tests = [
        ('find button where visible', "Visible buttons only"),
        ('find input where type="email"', "Email input fields"),
        ('find div where class contains "modal"', "Divs with 'modal' in class"),
        ('find button where text contains "Login"', "Login button"),
        ('find a where href contains "/about"', "About page link"),
    ]

    for command_str, description in tests:
        print(f"\n[ {description} ]")
        print(f"   Command: {command_str}")
        try:
            cmd = parser.parse(command_str)
            print(f"   [OK] Parsed successfully")
            print(f"      - Verb: {cmd.verb}")
            print(f"      - Target: {cmd.target.element_type}")
            print(f"      - Has condition: {cmd.condition_tree is not None}")
            if cmd.condition_tree:
                print(f"      - Condition type: {cmd.condition_tree.type}")
        except Exception as e:
            print(f"   [ERROR] {e}")

    # Section 3: Complex WHERE conditions
    print("\n" + "=" * 70)
    print("SECTION 3: Complex WHERE Conditions")
    print("=" * 70)

    tests = [
        ('find button where visible and enabled', "AND logic"),
        ('find input where type="email" or type="text"', "OR logic (email OR text)"),
        ('find a where visible and text contains "About"', "Multiple conditions"),
    ]

    for command_str, description in tests:
        print(f"\n[ {description} ]")
        print(f"   Command: {command_str}")
        try:
            cmd = parser.parse(command_str)
            print(f"   [OK] Parsed successfully")
            print(f"      - Verb: {cmd.verb}")
            print(f"      - Target: {cmd.target.element_type}")
            print(f"      - Condition: {cmd.condition_tree}")
        except Exception as e:
            print(f"   [ERROR] {e}")

    # Section 4: .find (Refine mode)
    print("\n" + "=" * 70)
    print("SECTION 4: .find - Refine Mode (Filter from temp)")
    print("=" * 70)

    print("\n[How refine mode works:]")
    print("   1. First use 'find' to query DOM -> results go to temp")
    print("   2. Then use '.find' to filter temp -> refines results")
    print("   3. Each '.find' reduces the temp results further")

    # Simulate workflow
    print("\n[ Step 1: Find all buttons ]")
    print("   Command: find button")
    cmd = parser.parse("find button")
    print(f"   [OK] Parsed - is_refine: {cmd.is_refine}")

    # Simulate: find all buttons
    all_buttons = [e for e in context.candidates if e.tag == 'button']
    context.temp = all_buttons
    print(f"   Result: {len(context.temp)} buttons found")

    print("\n[ Step 2: Refine to visible buttons only ]")
    print("   Command: .find where visible")
    cmd = parser.parse(".find where visible")
    print(f"   [OK] Parsed - is_refine: {cmd.is_refine}")

    # Simulate: refine to visible
    visible_buttons = [e for e in context.temp if e.visible]
    context.temp = visible_buttons
    print(f"   Result: {len(context.temp)} visible buttons")

    print("\n[ Step 3: Refine to primary class buttons ]")
    print("   Command: .find where class contains \"primary\"")
    cmd = parser.parse(".find where class contains \"primary\"")
    print(f"   [OK] Parsed - is_refine: {cmd.is_refine}")

    # Simulate: refine to primary
    primary_buttons = [e for e in context.temp if 'primary' in e.attributes.get('class', '')]
    context.temp = primary_buttons
    print(f"   Result: {len(context.temp)} primary buttons")

    # Section 5: Comparison Examples
    print("\n" + "=" * 70)
    print("SECTION 5: Regular FIND vs Refine Mode")
    print("=" * 70)

    print("\n[ Regular FIND (queries DOM every time) ]")
    print("   -> Always starts fresh from candidates")
    print("   -> Each command is independent")

    commands = [
        ("find button", "Scan entire page for buttons"),
        ("find input", "Scan entire page for inputs (ignores previous)"),
    ]

    for cmd, desc in commands:
        print(f"\n   {desc}")
        print(f"   Command: {cmd}")
        parsed = parser.parse(cmd)
        print(f"   -> is_refine: {parsed.is_refine}")

    print("\n[ Refine Mode (filters existing temp) ]")
    print("   -> Each .find refines the previous temp results")
    print("   -> Progressive filtering workflow")

    commands = [
        ("find button", "Step 1: Get all buttons -> temp"),
        (".find where visible", "Step 2: Filter visible from temp -> new temp"),
        (".find where text contains 'Login'", "Step 3: Filter 'Login' from temp -> final"),
    ]

    for cmd, desc in commands:
        print(f"\n   {desc}")
        print(f"   Command: {cmd}")
        parsed = parser.parse(cmd)
        print(f"   -> is_refine: {parsed.is_refine}")

    # Section 6: Common Patterns
    print("\n" + "=" * 70)
    print("SECTION 6: Common Patterns")
    print("=" * 70)

    patterns = [
        ("Basic element type", "find button"),
        ("With simple condition", "find button where visible"),
        ("With exact match", 'find input where type="submit"'),
        ("With contains", 'find div where class contains "modal"'),
        ("With text search", 'find a where text contains "Login"'),
        ("Multiple conditions (AND)", "find button where visible and enabled"),
        ("Refine mode", ".find where visible"),
        ("Refine with condition", ".find where text contains 'Submit'"),
        ("Complex refine", ".find where visible and enabled and text contains 'Save'"),
    ]

    for pattern, example in patterns:
        print(f"\n{pattern:35} -> {example}")

    # Summary
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)

    print("""
    1. Basic FIND: 'find button'
       -> Queries DOM, stores results in temp layer

    2. FIND with WHERE: 'find button where visible'
       -> Filters during DOM query

    3. .find (Refine): '.find where visible'
       -> Filters existing temp results (no DOM query)

    4. Chain refinements:
       find button        -> 15 buttons in temp
       .find where visible -> 12 visible buttons
       .find where enabled -> 10 enabled, visible buttons

    5. Common mistake:
       WRONG:  find button where visible where enabled
       CORRECT: find button where visible and enabled
    """)

    print("=" * 70)


if __name__ == "__main__":
    demo_find_syntax()
