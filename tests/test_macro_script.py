"""
Test Phase 4 Extended - Macro and Script Execution
"""
import sys
import os
import tempfile
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.parser import Parser
from src.core.macro import MacroManager


def test_macro_manager():
    """Test macro manager"""
    print("\n" + "="*60)
    print("Testing Macro Manager")
    print("="*60)

    manager = MacroManager()

    # Define macro
    print("\nTest: define macro")
    manager.define("test_macro", ["add input", "list"])
    assert manager.exists("test_macro")
    print("  [OK] Macro defined")

    # Get macro
    print("\nTest: get macro")
    commands = manager.get("test_macro")
    assert commands == ["add input", "list"]
    print(f"  [OK] Got commands: {commands}")

    # List macros
    print("\nTest: list all macros")
    all_macros = manager.list_all()
    assert "test_macro" in all_macros
    print(f"  [OK] Listed {len(all_macros)} macro(s)")

    # Delete macro
    print("\nTest: delete macro")
    manager.delete("test_macro")
    assert not manager.exists("test_macro")
    print("  [OK] Macro deleted")

    print("\n[OK] Macro manager tests passed")
    return True


def test_parser_macro_commands():
    """Test parsing macro commands"""
    print("\n" + "="*60)
    print("Testing Macro Command Parsing")
    print("="*60)

    parser = Parser()

    tests = [
        ("macro test add input", "macro", "test:add input"),
        ("macro analyze list button", "macro", "analyze:list button"),
        ("run test", "run", "test"),
        ("run analyze", "run", "analyze"),
        ("macros", "macros", None),
        ("exec test.sel", "exec", "test.sel"),
        ("exec script/run.sel", "exec", "script/run.sel"),
    ]

    for test_input, expected_verb, expected_arg in tests:
        print(f"\nInput: {test_input}")
        cmd = parser.parse(test_input)

        assert cmd.verb == expected_verb, f"Expected verb '{expected_verb}', got {cmd.verb}"
        if expected_arg is not None:
            assert cmd.argument == expected_arg, f"Expected argument '{expected_arg}', got '{cmd.argument}'"
        print(f"  [OK] verb={cmd.verb}, argument={cmd.argument}")

    print("\n[OK] Macro command parsing tests passed")
    return True


def test_script_file_creation():
    """Test script file creation and reading"""
    print("\n" + "="*60)
    print("Testing Script File Creation")
    print("="*60)

    # Create temp script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sel', delete=False, encoding='utf-8') as f:
        f.write("# Test script\n")
        f.write("scan\n")
        f.write("add input\n")
        f.write("\n")
        f.write("# Add button\n")
        f.write("add button\n")
        f.write("list\n")
        script_path = f.name

    try:
        # Read and verify
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"\nScript file created: {script_path}")
        print(f"Lines: {len(lines)}")

        # Count non-comment, non-empty lines
        command_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        print(f"Command lines: {len(command_lines)}")
        assert len(command_lines) == 4  # scan, add input, add button, list

        print("  [OK] Script file created and verified")

    finally:
        # Cleanup
        os.unlink(script_path)

    print("\n[OK] Script file tests passed")
    return True


def test_macro_definition_edge_cases():
    """Test edge cases for macro definition"""
    print("\n" + "="*60)
    print("Testing Macro Edge Cases")
    print("="*60)

    manager = MacroManager()

    # Empty name
    print("\nTest: empty name")
    try:
        manager.define("", ["add input"])
        assert False, "Should raise error"
    except ValueError:
        print("  [OK] Correctly raises error for empty name")

    # Empty commands
    print("\nTest: empty commands")
    try:
        manager.define("test", [])
        assert False, "Should raise error"
    except ValueError:
        print("  [OK] Correctly raises error for empty commands")

    # Get nonexistent macro
    print("\nTest: get nonexistent macro")
    try:
        manager.get("nonexistent")
        assert False, "Should raise error"
    except KeyError:
        print("  [OK] Correctly raises error for nonexistent macro")

    # Delete nonexistent macro
    print("\nTest: delete nonexistent macro")
    try:
        manager.delete("nonexistent")
        assert False, "Should raise error"
    except KeyError:
        print("  [OK] Correctly raises error when deleting nonexistent")

    print("\n[OK] Edge case tests passed")
    return True


def test_complex_macro_commands():
    """Test complex macro command strings"""
    print("\n" + "="*60)
    print("Testing Complex Macro Commands")
    print("="*60)

    parser = Parser()

    tests = [
        ('macro login add input where type="email"', "macro", 'login:add input where type="email"'),
        ('macro filter list where visible', "macro", 'filter:list where visible'),
        # Note: multi-command macros with semicolons would require semicolon token
        # ('macro save_all add all; save collection', "macro", 'save_all:add all; save collection'),
    ]

    for test_input, expected_verb, expected_arg in tests:
        print(f"\nInput: {test_input}")
        cmd = parser.parse(test_input)

        assert cmd.verb == expected_verb
        assert cmd.argument == expected_arg
        print(f"  [OK] Parsed correctly")

    print("\n[OK] Complex macro command tests passed")
    return True


if __name__ == '__main__':
    success = True
    success = test_macro_manager() and success
    success = test_parser_macro_commands() and success
    success = test_script_file_creation() and success
    success = test_macro_definition_edge_cases() and success
    success = test_complex_macro_commands() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL MACRO AND SCRIPT TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
