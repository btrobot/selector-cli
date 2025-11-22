"""
Test Phase 2 integration - complex condition evaluation
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.parser import Parser
from src.commands.executor import CommandExecutor
from src.core.element import Element
from src.core.context import Context


def create_test_elements():
    """Create test elements with various properties"""
    elements = [
        Element(
            index=0,
            uuid="elem-0",
            tag="input",
            selector='input[type="text"]',
            type="text",
            id="username",
            name="user_name",
            placeholder="Enter name",
            text="",
            attributes={"type": "text", "id": "username", "name": "user_name"}
        ),
        Element(
            index=1,
            uuid="elem-1",
            tag="input",
            selector='input[type="email"]',
            type="email",
            id="email",
            name="user_email",
            placeholder="Enter email",
            text="",
            attributes={"type": "email", "id": "email", "name": "user_email"}
        ),
        Element(
            index=2,
            uuid="elem-2",
            tag="input",
            selector='input[type="password"]',
            type="password",
            id="password",
            name="user_password",
            placeholder="",
            text="",
            attributes={"type": "password", "id": "password", "name": "user_password"}
        ),
        Element(
            index=3,
            uuid="elem-3",
            tag="button",
            selector='button[type="submit"]',
            type="submit",
            id="submit-btn",
            name="",
            placeholder="",
            text="Submit Form",
            attributes={"type": "submit", "id": "submit-btn"}
        ),
        Element(
            index=4,
            uuid="elem-4",
            tag="button",
            selector='button',
            type="button",
            id="cancel-btn",
            name="",
            placeholder="",
            text="Cancel",
            attributes={"type": "button", "id": "cancel-btn"}
        ),
        Element(
            index=5,
            uuid="elem-5",
            tag="input",
            selector='input[type="text"]',
            type="text",
            id="first_name",
            name="first_name",
            placeholder="First name",
            text="",
            attributes={"type": "text", "id": "first_name", "name": "first_name"}
        ),
        Element(
            index=6,
            uuid="elem-6",
            tag="input",
            selector='input[type="text"]',
            type="text",
            id="last_name",
            name="last_name",
            placeholder="Last name",
            text="",
            attributes={"type": "text", "id": "last_name", "name": "last_name"}
        ),
    ]
    return elements


def test_and_operator():
    """Test AND operator in conditions"""
    print("\n" + "="*60)
    print("Testing AND Operator")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Parse command
    cmd = parser.parse('add input where type="text" and name="user_name"')
    print(f"Command: add input where type=\"text\" and name=\"user_name\"")
    print(f"Condition tree: {cmd.condition_tree}")

    # Create test context
    elements = create_test_elements()

    # Manually evaluate condition
    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"\nFiltered elements: {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} type={elem.type} name={elem.name}")

    # Verify: should match only index 0 (username input with type=text and name=user_name)
    assert len(filtered) == 1, f"Expected 1 element, got {len(filtered)}"
    assert filtered[0].index == 0, f"Expected index 0, got {filtered[0].index}"
    assert filtered[0].type == "text", f"Expected type text, got {filtered[0].type}"
    assert filtered[0].name == "user_name", f"Expected name user_name, got {filtered[0].name}"

    print("[OK] AND operator works correctly")
    return True


def test_or_operator():
    """Test OR operator in conditions"""
    print("\n" + "="*60)
    print("Testing OR Operator")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Parse command
    cmd = parser.parse('add input where type="text" or type="email"')
    print(f"Command: add input where type=\"text\" or type=\"email\"")
    print(f"Condition tree: {cmd.condition_tree}")

    # Create test context
    elements = create_test_elements()

    # Manually evaluate condition
    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"\nFiltered elements: {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} type={elem.type}")

    # Verify: should match indices 0, 1, 5, 6 (text or email inputs)
    assert len(filtered) == 4, f"Expected 4 elements, got {len(filtered)}"
    assert filtered[0].type in ["text", "email"], f"Expected text or email type"

    print("[OK] OR operator works correctly")
    return True


def test_not_operator():
    """Test NOT operator in conditions"""
    print("\n" + "="*60)
    print("Testing NOT Operator")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Parse command
    cmd = parser.parse('add button where not type="submit"')
    print(f"Command: add button where not type=\"submit\"")
    print(f"Condition tree: {cmd.condition_tree}")

    # Create test context
    elements = create_test_elements()

    # Manually evaluate condition
    filtered = []
    for elem in elements:
        if elem.tag == "button":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"\nFiltered elements: {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} type={elem.type}")

    # Verify: should match index 4 (button with type=button, not submit)
    assert len(filtered) == 1, f"Expected 1 element, got {len(filtered)}"
    assert filtered[0].index == 4, f"Expected index 4, got {filtered[0].index}"
    assert filtered[0].type == "button", f"Expected type button, got {filtered[0].type}"

    print("[OK] NOT operator works correctly")
    return True


def test_comparison_operators():
    """Test comparison operators (>, >=, <, <=)"""
    print("\n" + "="*60)
    print("Testing Comparison Operators")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Test > operator
    cmd = parser.parse('list where index > 3')
    print(f"Command: list where index > 3")

    elements = create_test_elements()
    filtered = []
    for elem in elements:
        if executor._evaluate_condition_tree(elem, cmd.condition_tree):
            filtered.append(elem)

    print(f"Filtered elements (index > 3): {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag}")

    # Verify: should match indices 4, 5, 6
    assert len(filtered) == 3, f"Expected 3 elements, got {len(filtered)}"
    assert all(elem.index > 3 for elem in filtered), "All indices should be > 3"

    # Test <= operator
    cmd = parser.parse('list where index <= 2')
    print(f"\nCommand: list where index <= 2")

    filtered = []
    for elem in elements:
        if executor._evaluate_condition_tree(elem, cmd.condition_tree):
            filtered.append(elem)

    print(f"Filtered elements (index <= 2): {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag}")

    # Verify: should match indices 0, 1, 2
    assert len(filtered) == 3, f"Expected 3 elements, got {len(filtered)}"
    assert all(elem.index <= 2 for elem in filtered), "All indices should be <= 2"

    print("[OK] Comparison operators work correctly")
    return True


def test_string_operators():
    """Test string operators (contains, starts, ends)"""
    print("\n" + "="*60)
    print("Testing String Operators")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Test CONTAINS
    cmd = parser.parse('add button where text contains "mit"')
    print(f"Command: add button where text contains \"mit\"")

    elements = create_test_elements()
    filtered = []
    for elem in elements:
        if elem.tag == "button":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"Filtered elements (text contains 'mit'): {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} text={elem.text}")

    # Verify: should match index 3 (Submit Form button)
    assert len(filtered) == 1, f"Expected 1 element, got {len(filtered)}"
    assert "mit" in filtered[0].text, "Text should contain 'mit'"

    # Test STARTS
    cmd = parser.parse('add input where id starts "user"')
    print(f"\nCommand: add input where id starts \"user\"")

    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"Filtered elements (id starts 'user'): {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} id={elem.id}")

    # Verify: should match only index 0 (username - only one with id starting with "user")
    assert len(filtered) == 1, f"Expected 1 element, got {len(filtered)}"
    assert filtered[0].id.startswith("user"), "Id should start with 'user'"

    # Test ENDS
    cmd = parser.parse('add input where name ends "_name"')
    print(f"\nCommand: add input where name ends \"_name\"")

    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"Filtered elements (name ends '_name'): {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} name={elem.name}")

    # Verify: should match indices 0, 5, 6 (user_name, first_name, last_name)
    assert len(filtered) == 3, f"Expected 3 elements, got {len(filtered)}"
    assert all(elem.name.endswith("_name") for elem in filtered), "All names should end with '_name'"

    print("[OK] String operators work correctly")
    return True


def test_complex_nested_conditions():
    """Test complex nested conditions with parentheses"""
    print("\n" + "="*60)
    print("Testing Complex Nested Conditions")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Parse command
    cmd = parser.parse('add input where (type="text" or type="email") and id starts "user"')
    print(f"Command: add input where (type=\"text\" or type=\"email\") and id starts \"user\"")
    print(f"Condition tree: {cmd.condition_tree}")

    # Create test context
    elements = create_test_elements()

    # Manually evaluate condition
    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"\nFiltered elements: {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} type={elem.type} id={elem.id}")

    # Verify: should match only index 0 (username with type=text and id starts with user)
    # Note: index 1 (email) has id="email" which does NOT start with "user"
    assert len(filtered) == 1, f"Expected 1 element, got {len(filtered)}"
    assert filtered[0].type in ["text", "email"], "Should be text or email"
    assert filtered[0].id.startswith("user"), "Id should start with user"

    print("[OK] Complex nested conditions work correctly")
    return True


def test_operator_precedence():
    """Test operator precedence is correct"""
    print("\n" + "="*60)
    print("Testing Operator Precedence")
    print("="*60)

    parser = Parser()
    executor = CommandExecutor()

    # Test: a or b and c should be: a or (b and c)
    cmd = parser.parse('add input where type="email" or type="text" and name="user_name"')
    print(f"Command: add input where type=\"email\" or type=\"text\" and name=\"user_name\"")
    print(f"Expected: (type=email) OR (type=text AND name=user_name)")

    elements = create_test_elements()
    filtered = []
    for elem in elements:
        if elem.tag == "input":
            if executor._evaluate_condition_tree(elem, cmd.condition_tree):
                filtered.append(elem)

    print(f"\nFiltered elements: {len(filtered)}")
    for elem in filtered:
        print(f"  [{elem.index}] {elem.tag} type={elem.type} name={elem.name}")

    # Verify: should match indices 0 (type=text and name=user_name) and 1 (type=email)
    assert len(filtered) == 2, f"Expected 2 elements, got {len(filtered)}"
    assert any(elem.type == "email" for elem in filtered), "Should include email type"
    assert any(elem.type == "text" and elem.name == "user_name" for elem in filtered), "Should include text with user_name"

    print("[OK] Operator precedence is correct")
    return True


if __name__ == '__main__':
    success = True
    success = test_and_operator() and success
    success = test_or_operator() and success
    success = test_not_operator() and success
    success = test_comparison_operators() and success
    success = test_string_operators() and success
    success = test_complex_nested_conditions() and success
    success = test_operator_precedence() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL PHASE 2 INTEGRATION TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
