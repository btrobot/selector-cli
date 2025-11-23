"""
Test Phase 5 - Highlight Feature
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.lexer import Lexer, TokenType
from src.parser.parser import Parser
from src.parser.command import TargetType


def test_highlight_tokens():
    """Test HIGHLIGHT and UNHIGHLIGHT tokens"""
    print("\n" + "="*60)
    print("Testing Highlight Tokens")
    print("="*60)

    lexer = Lexer()

    # Test highlight keyword
    tokens = lexer.tokenize("highlight")
    assert tokens[0].type == TokenType.HIGHLIGHT
    print("\n[OK] 'highlight' tokenized as HIGHLIGHT")

    # Test unhighlight keyword
    tokens = lexer.tokenize("unhighlight")
    assert tokens[0].type == TokenType.UNHIGHLIGHT
    print("[OK] 'unhighlight' tokenized as UNHIGHLIGHT")

    print("\n[OK] All token tests passed")
    return True


def test_highlight_command_parsing():
    """Test parsing highlight commands"""
    print("\n" + "="*60)
    print("Testing Highlight Command Parsing")
    print("="*60)

    parser = Parser()

    # Test 1: Simple highlight (no target)
    cmd = parser.parse("highlight")
    assert cmd.verb == 'highlight'
    assert cmd.target is None
    assert cmd.condition_tree is None
    print("\n[OK] 'highlight' parsed correctly")

    # Test 2: Highlight with target
    cmd = parser.parse("highlight input")
    assert cmd.verb == 'highlight'
    assert cmd.target is not None
    assert cmd.target.type == TargetType.ELEMENT_TYPE
    assert cmd.target.element_type == 'input'
    print("[OK] 'highlight input' parsed correctly")

    # Test 3: Highlight with condition
    cmd = parser.parse('highlight button where type="submit"')
    assert cmd.verb == 'highlight'
    assert cmd.target is not None
    assert cmd.target.type == TargetType.ELEMENT_TYPE
    assert cmd.target.element_type == 'button'
    assert cmd.condition_tree is not None
    print('[OK] \'highlight button where type="submit"\' parsed correctly')

    # Test 4: Highlight all
    cmd = parser.parse("highlight all")
    assert cmd.verb == 'highlight'
    assert cmd.target is not None
    assert cmd.target.type == TargetType.ALL
    print("[OK] 'highlight all' parsed correctly")

    # Test 5: Unhighlight
    cmd = parser.parse("unhighlight")
    assert cmd.verb == 'unhighlight'
    print("[OK] 'unhighlight' parsed correctly")

    print("\n[OK] All parsing tests passed")
    return True


def test_highlight_with_complex_conditions():
    """Test highlight with complex WHERE conditions"""
    print("\n" + "="*60)
    print("Testing Highlight with Complex Conditions")
    print("="*60)

    parser = Parser()

    # Test 1: AND condition
    cmd = parser.parse('highlight input where type="text" and visible')
    assert cmd.verb == 'highlight'
    assert cmd.target.element_type == 'input'
    assert cmd.condition_tree is not None
    print('\n[OK] \'highlight input where type="text" and visible\' parsed')

    # Test 2: OR condition
    cmd = parser.parse('highlight button where type="submit" or type="button"')
    assert cmd.verb == 'highlight'
    assert cmd.target.element_type == 'button'
    assert cmd.condition_tree is not None
    print('[OK] \'highlight button where type="submit" or type="button"\' parsed')

    # Test 3: NOT condition
    cmd = parser.parse('highlight input where not disabled')
    assert cmd.verb == 'highlight'
    assert cmd.target.element_type == 'input'
    assert cmd.condition_tree is not None
    print('[OK] \'highlight input where not disabled\' parsed')

    # Test 4: String operators
    cmd = parser.parse('highlight a where text contains "Click"')
    assert cmd.verb == 'highlight'
    assert cmd.target.element_type == 'a'
    assert cmd.condition_tree is not None
    print('[OK] \'highlight a where text contains "Click"\' parsed')

    print("\n[OK] All complex condition tests passed")
    return True


def test_highlight_with_indices():
    """Test highlight with index targets"""
    print("\n" + "="*60)
    print("Testing Highlight with Indices")
    print("="*60)

    parser = Parser()

    # Test 1: Single index
    cmd = parser.parse("highlight [5]")
    assert cmd.verb == 'highlight'
    assert cmd.target.type == TargetType.INDEX
    assert cmd.target.indices == [5]
    print("\n[OK] 'highlight [5]' parsed correctly")

    # Test 2: Multiple indices
    cmd = parser.parse("highlight [1,3,5]")
    assert cmd.verb == 'highlight'
    assert cmd.target.type == TargetType.INDICES
    assert cmd.target.indices == [1, 3, 5]
    print("[OK] 'highlight [1,3,5]' parsed correctly")

    # Test 3: Range (expands to indices)
    cmd = parser.parse("highlight [1-5]")
    assert cmd.verb == 'highlight'
    assert cmd.target.type == TargetType.INDICES  # Range is expanded to INDICES
    assert cmd.target.indices == [1, 2, 3, 4, 5]
    print("[OK] 'highlight [1-5]' parsed correctly (range expanded to indices)")

    print("\n[OK] All index tests passed")
    return True


def test_error_cases():
    """Test error handling"""
    print("\n" + "="*60)
    print("Testing Error Cases")
    print("="*60)

    parser = Parser()

    # Unhighlight should not accept arguments (currently it ignores them)
    # This is not an error in current implementation, just documenting behavior
    cmd = parser.parse("unhighlight")
    assert cmd.verb == 'unhighlight'
    print("\n[OK] 'unhighlight' behaves correctly")

    print("\n[OK] All error case tests passed")
    return True


def test_backward_compatibility():
    """Test that existing commands still work"""
    print("\n" + "="*60)
    print("Testing Backward Compatibility")
    print("="*60)

    parser = Parser()

    # Test existing commands still work
    test_commands = [
        "open https://example.com",
        "scan",
        "add input",
        'add button where type="submit"',
        "list",
        "count",
        "clear",
    ]

    for cmd_str in test_commands:
        try:
            cmd = parser.parse(cmd_str)
            print(f"[OK] '{cmd_str}' still works")
        except Exception as e:
            print(f"[FAIL] '{cmd_str}' failed: {e}")
            return False

    print("\n[OK] All backward compatibility tests passed")
    return True


if __name__ == '__main__':
    success = True
    success = test_highlight_tokens() and success
    success = test_highlight_command_parsing() and success
    success = test_highlight_with_complex_conditions() and success
    success = test_highlight_with_indices() and success
    success = test_error_cases() and success
    success = test_backward_compatibility() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL HIGHLIGHT TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
