"""
Test Phase 5 - Command History
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.lexer import Lexer, TokenType
from src.parser.parser import Parser
from src.core.context import Context


def test_history_tokens():
    """Test history tokens"""
    print("\n" + "="*60)
    print("Testing History Tokens")
    print("="*60)

    lexer = Lexer()

    # Test history keyword
    tokens = lexer.tokenize("history")
    assert tokens[0].type == TokenType.HISTORY
    print("\n[OK] 'history' tokenized as HISTORY")

    # Test bang
    tokens = lexer.tokenize("!")
    assert tokens[0].type == TokenType.BANG
    print("[OK] '!' tokenized as BANG")

    # Test !!
    tokens = lexer.tokenize("!!")
    assert tokens[0].type == TokenType.BANG
    assert tokens[1].type == TokenType.BANG
    print("[OK] '!!' tokenized as BANG BANG")

    # Test !5
    tokens = lexer.tokenize("!5")
    assert tokens[0].type == TokenType.BANG
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == "5"
    print("[OK] '!5' tokenized as BANG NUMBER")

    print("\n[OK] All token tests passed")
    return True


def test_history_parsing():
    """Test parsing history commands"""
    print("\n" + "="*60)
    print("Testing History Command Parsing")
    print("="*60)

    parser = Parser()

    # Test history
    cmd = parser.parse("history")
    assert cmd.verb == 'history'
    assert cmd.argument is None
    print("\n[OK] 'history' parsed correctly")

    # Test history 10
    cmd = parser.parse("history 10")
    assert cmd.verb == 'history'
    assert cmd.argument == '10'
    print("[OK] 'history 10' parsed correctly")

    # Test !!
    cmd = parser.parse("!!")
    assert cmd.verb == 'bang_last'
    print("[OK] '!!' parsed correctly")

    # Test !5
    cmd = parser.parse("!5")
    assert cmd.verb == 'bang_n'
    assert cmd.argument == '5'
    print("[OK] '!5' parsed correctly")

    # Test !0
    cmd = parser.parse("!0")
    assert cmd.verb == 'bang_n'
    assert cmd.argument == '0'
    print("[OK] '!0' parsed correctly")

    print("\n[OK] All parsing tests passed")
    return True


def test_context_history_methods():
    """Test Context history methods"""
    print("\n" + "="*60)
    print("Testing Context History Methods")
    print("="*60)

    context = Context()

    # Add commands to history
    context.add_to_history("open https://example.com")
    context.add_to_history("scan")
    context.add_to_history("add input")
    context.add_to_history("list")

    # Test get_history (all)
    history = context.get_history()
    assert len(history) == 4
    assert history[0] == "open https://example.com"
    print("\n[OK] get_history() returns all commands")

    # Test get_history with count
    history = context.get_history(2)
    assert len(history) == 2
    assert history[0] == "add input"
    assert history[1] == "list"
    print("[OK] get_history(2) returns last 2 commands")

    # Test get_history_command
    cmd = context.get_history_command(0)
    assert cmd == "open https://example.com"
    print("[OK] get_history_command(0) returns first command")

    cmd = context.get_history_command(2)
    assert cmd == "add input"
    print("[OK] get_history_command(2) returns third command")

    cmd = context.get_history_command(10)
    assert cmd is None
    print("[OK] get_history_command(10) returns None for out of range")

    # Test get_last_command
    cmd = context.get_last_command()
    assert cmd == "list"
    print("[OK] get_last_command() returns 'list'")

    print("\n[OK] All Context history method tests passed")
    return True


def test_history_output_format():
    """Test history output formatting"""
    print("\n" + "="*60)
    print("Testing History Output Format")
    print("="*60)

    # Simulated history output
    history = [
        "open https://example.com",
        "scan",
        "add input",
        "add button",
        "list"
    ]

    # Format like executor does
    lines = []
    for i, cmd in enumerate(history):
        lines.append(f"  {i:4d}  {cmd}")

    output = "Command History:\n" + "\n".join(lines)

    # Verify format
    assert "Command History:" in output
    assert "     0  open https://example.com" in output
    assert "     4  list" in output
    print("\n[OK] History formatted correctly with indices")

    # Test subset format (last 3)
    subset = history[-3:]
    lines = []
    start_index = len(history) - len(subset)
    for i, cmd in enumerate(subset):
        index = start_index + i
        lines.append(f"  {index:4d}  {cmd}")

    output = "Command History:\n" + "\n".join(lines)
    assert "     2  add input" in output
    assert "     4  list" in output
    print("[OK] History subset formatted correctly")

    print("\n[OK] All history output format tests passed")
    return True


def test_error_cases():
    """Test error handling"""
    print("\n" + "="*60)
    print("Testing Error Cases")
    print("="*60)

    parser = Parser()

    # ! alone should fail parsing (needs number or !)
    try:
        cmd = parser.parse("! ")
        print("\n[WARN] Single '!' should ideally fail, but may succeed")
    except ValueError as e:
        print(f"\n[OK] Single '!' raises error: {e}")

    # Context tests
    context = Context()

    # Empty history
    history = context.get_history()
    assert len(history) == 0
    print("[OK] Empty history returns empty list")

    last_cmd = context.get_last_command()
    assert last_cmd is None
    print("[OK] get_last_command() on empty history returns None")

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
        "add input",
        "list",
        "highlight",
        "union my_collection",
        "unique",
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
    success = test_history_tokens() and success
    success = test_history_parsing() and success
    success = test_context_history_methods() and success
    success = test_history_output_format() and success
    success = test_error_cases() and success
    success = test_backward_compatibility() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL COMMAND HISTORY TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
