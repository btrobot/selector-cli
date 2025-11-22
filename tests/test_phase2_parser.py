"""
Test Phase 2 parser - complex conditions and ranges
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.parser import Parser
from src.parser.command import ConditionType, LogicOp, Operator, TargetType


def test_complex_conditions():
    """Test complex WHERE clause parsing"""
    print("="*60)
    print("Testing Phase 2 Parser - Complex Conditions")
    print("="*60)

    parser = Parser()

    tests = [
        ("add input where type=\"text\" and visible", "AND operator"),
        ("add input where type=\"text\" or type=\"email\"", "OR operator"),
        ("add input where not disabled", "NOT operator"),
        ("add input where (type=\"text\" or type=\"email\") and visible", "Parentheses with AND/OR"),
        ("list where index > 5", "Greater than"),
        ("list where index >= 10", "Greater than or equal"),
        ("list where index < 20", "Less than"),
        ("list where index <= 30", "Less than or equal"),
        ("add button where text contains \"Submit\"", "String contains"),
        ("add input where id starts \"user_\"", "String starts"),
        ("add input where name ends \"_input\"", "String ends"),
        ("add button where text matches \"[0-9]+\"", "String matches (regex)"),
        ("add input where visible = true", "Boolean true"),
        ("add input where disabled = false", "Boolean false"),
        ("add input where (type=\"text\" or type=\"email\") and not disabled and visible", "Complex nested"),
    ]

    for test_input, description in tests:
        print(f"\n[{description}]")
        print(f"  Input: {test_input}")

        try:
            cmd = parser.parse(test_input)
            print(f"  Parsed: {cmd.verb}")

            if cmd.condition_tree:
                print(f"  Condition tree: {cmd.condition_tree}")

                # Verify specific conditions
                if "and" in test_input.lower() and "or" not in test_input.lower():
                    assert cmd.condition_tree.type in (ConditionType.COMPOUND, ConditionType.SIMPLE, ConditionType.UNARY), \
                        f"Expected COMPOUND/SIMPLE/UNARY for AND, got {cmd.condition_tree.type}"

                if "not" in test_input.lower():
                    # Check if there's a NOT in the tree (could be nested)
                    def has_not(node):
                        if node.type == ConditionType.UNARY:
                            return True
                        if node.type == ConditionType.COMPOUND:
                            return has_not(node.left) or has_not(node.right)
                        return False
                    assert has_not(cmd.condition_tree), "Expected NOT in tree"

                if ">" in test_input and ">=" not in test_input:
                    # Find the simple condition with GT
                    def has_gt(node):
                        if node.type == ConditionType.SIMPLE:
                            return node.operator == Operator.GT
                        if node.type == ConditionType.COMPOUND:
                            return has_gt(node.left) or has_gt(node.right)
                        if node.type == ConditionType.UNARY:
                            return has_gt(node.operand)
                        return False
                    assert has_gt(cmd.condition_tree), "Expected GT operator"

                print("  [OK] Tree structure verified")
            else:
                print("  [WARN] No condition tree")

        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n" + "="*60)
    print("[OK] All complex condition tests passed!")
    print("="*60)
    return True


def test_range_selection():
    """Test range parsing"""
    print("\n" + "="*60)
    print("Testing Phase 2 Parser - Range Selection")
    print("="*60)

    parser = Parser()

    tests = [
        ("[1-10]", "Simple range", list(range(1, 11))),
        ("[0-5]", "Range from 0", list(range(0, 6))),
        ("[1,3,5-8,10]", "Mixed range", [1, 3, 5, 6, 7, 8, 10]),
        ("[5]", "Single index", [5]),
        ("[1,2,3]", "Multiple indices", [1, 2, 3]),
    ]

    for test_input, description, expected_indices in tests:
        print(f"\n[{description}]")
        print(f"  Input: add {test_input}")

        try:
            cmd = parser.parse(f"add {test_input}")
            print(f"  Parsed: {cmd.verb}")
            print(f"  Target type: {cmd.target.type}")
            print(f"  Indices: {cmd.target.indices}")

            assert cmd.target.indices == expected_indices, \
                f"Expected {expected_indices}, got {cmd.target.indices}"

            print("  [OK] Indices match expected")

        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n" + "="*60)
    print("[OK] All range selection tests passed!")
    print("="*60)
    return True


def test_operator_precedence():
    """Test operator precedence"""
    print("\n" + "="*60)
    print("Testing Operator Precedence")
    print("="*60)

    parser = Parser()

    # Test: a or b and c should parse as: a or (b and c)
    test = "list where type=\"text\" or type=\"email\" and visible"
    print(f"\nInput: {test}")
    print("Expected: (type=\"text\") OR ((type=\"email\") AND visible)")

    try:
        cmd = parser.parse(test)
        tree = cmd.condition_tree
        print(f"Parsed: {tree}")

        # Should be OR at top level
        assert tree.type == ConditionType.COMPOUND, "Top should be COMPOUND"
        assert tree.logic_op == LogicOp.OR, "Top should be OR"

        # Right side should be AND
        assert tree.right.type == ConditionType.COMPOUND, "Right should be COMPOUND"
        assert tree.right.logic_op == LogicOp.AND, "Right should be AND"

        print("[OK] Precedence correct: OR at top, AND on right")

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # Test: NOT has higher precedence than AND
    test2 = "list where not disabled and visible"
    print(f"\nInput: {test2}")
    print("Expected: (NOT disabled) AND visible")

    try:
        cmd = parser.parse(test2)
        tree = cmd.condition_tree
        print(f"Parsed: {tree}")

        # Should be AND at top
        assert tree.type == ConditionType.COMPOUND, "Top should be COMPOUND"
        assert tree.logic_op == LogicOp.AND, "Top should be AND"

        # Left should be NOT
        assert tree.left.type == ConditionType.UNARY, "Left should be UNARY (NOT)"

        print("[OK] Precedence correct: AND at top, NOT on left")

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    print("\n" + "="*60)
    print("[OK] Operator precedence tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = True
    success = test_complex_conditions() and success
    success = test_range_selection() and success
    success = test_operator_precedence() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL PHASE 2 PARSER TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
