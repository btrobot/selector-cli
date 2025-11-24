"""
Test script for Selector CLI Phase 1 MVP
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from selector_cli.parser.lexer import Lexer
from selector_cli.parser.parser import Parser


def test_lexer():
    """Test lexer"""
    print("Testing Lexer...")

    lexer = Lexer()

    # Test simple commands
    tests = [
        "open https://example.com",
        "scan",
        "add input",
        "add button where type=\"submit\"",
        "list",
        "show [0]",
        "count",
        "quit"
    ]

    for test in tests:
        print(f"\n  Input: {test}")
        try:
            tokens = lexer.tokenize(test)
            print(f"  Tokens: {[f'{t.type.name}({t.value})' for t in tokens[:-1]]}")  # Skip EOF
        except Exception as e:
            print(f"  Error: {e}")

    print("\n[OK] Lexer test complete\n")


def test_parser():
    """Test parser"""
    print("Testing Parser...")

    parser = Parser()

    tests = [
        "open https://example.com",
        "scan",
        "add input",
        "add button where type=\"submit\"",
        "add [1,2,3]",
        "list",
        "list input",
        "list where type=\"email\"",
        "show",
        "show [0]",
        "remove [5]",
        "clear",
        "count",
        "help",
        "quit"
    ]

    for test in tests:
        print(f"\n  Input: {test}")
        try:
            command = parser.parse(test)
            print(f"  Command: verb={command.verb}, target={command.target}, condition={command.condition}")
        except Exception as e:
            print(f"  Error: {e}")

    print("\n[OK] Parser test complete\n")


def test_command_structures():
    """Test command data structures"""
    print("Testing Command Structures...")

    from selector_cli.parser.command import Command, Target, TargetType, Condition, Operator

    # Test Target
    target1 = Target(type=TargetType.ELEMENT_TYPE, element_type="input")
    print(f"  Target 1: {target1}")

    target2 = Target(type=TargetType.INDEX, indices=[0])
    print(f"  Target 2: {target2}")

    # Test Condition
    condition = Condition(field="type", operator=Operator.EQUALS, value="email")
    print(f"  Condition: {condition.field} {condition.operator.name} {condition.value}")

    # Test Command
    command = Command(verb="add", target=target1, condition=condition)
    print(f"  Command: {command}")

    print("\n[OK] Command structures test complete\n")


if __name__ == '__main__':
    print("="*60)
    print("Selector CLI - Phase 1 MVP Test Suite")
    print("="*60)
    print()

    test_lexer()
    test_parser()
    test_command_structures()

    print("="*60)
    print("All tests complete!")
    print("="*60)
    print()
    print("To run the interactive CLI:")
    print("  python selector-cli.py")
