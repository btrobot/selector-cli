#!/usr/bin/env python
"""
Test parameterized macros
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.macro import MacroManager, Macro


def test_basic_macro():
    """Test basic macro without parameters"""
    print("\n1. Testing basic macro (no parameters)...")

    mm = MacroManager()
    mm.define("quick-scan", ["scan", "add input", "list"])

    macro = mm.get("quick-scan")
    assert macro.name == "quick-scan"
    assert len(macro.parameters) == 0
    assert len(macro.commands) == 3

    commands = mm.run("quick-scan", [])
    assert len(commands) == 3
    assert commands[0] == "scan"
    assert commands[1] == "add input"
    assert commands[2] == "list"

    print("   [OK] Basic macro works")


def test_macro_with_single_param():
    """Test macro with single parameter"""
    print("\n2. Testing macro with single parameter...")

    mm = MacroManager()
    mm.define("open-and-scan", ["open {url}", "scan"], ["url"])

    macro = mm.get("open-and-scan")
    assert macro.name == "open-and-scan"
    assert macro.parameters == ["url"]

    commands = mm.run("open-and-scan", ["https://example.com"])
    assert len(commands) == 2
    assert commands[0] == "open https://example.com"
    assert commands[1] == "scan"

    print("   [OK] Single parameter macro works")


def test_macro_with_multiple_params():
    """Test macro with multiple parameters"""
    print("\n3. Testing macro with multiple parameters...")

    mm = MacroManager()
    mm.define(
        "login-form",
        ["add input where name='{username_field}'", "add input where name='{password_field}'", "list"],
        ["username_field", "password_field"]
    )

    macro = mm.get("login-form")
    assert macro.name == "login-form"
    assert len(macro.parameters) == 2

    commands = mm.run("login-form", ["user", "pass"])
    assert len(commands) == 3
    assert commands[0] == "add input where name='user'"
    assert commands[1] == "add input where name='pass'"
    assert commands[2] == "list"

    print("   [OK] Multiple parameters macro works")


def test_parameter_validation():
    """Test parameter count validation"""
    print("\n4. Testing parameter validation...")

    mm = MacroManager()
    mm.define("test", ["open {url}"], ["url"])

    try:
        # Too few arguments
        mm.run("test", [])
        print("   [FAIL] Should have raised ValueError for too few arguments")
        return False
    except ValueError as e:
        assert "expects 1 parameters" in str(e)
        print("   [OK] Correctly validates too few arguments")

    try:
        # Too many arguments (should work - extra args ignored)
        commands = mm.run("test", ["https://example.com", "extra"])
        assert len(commands) == 1
        assert commands[0] == "open https://example.com"
        print("   [OK] Extra arguments ignored")
    except Exception as e:
        print(f"   [FAIL] Too many arguments should work: {e}")
        return False

    return True


def test_macro_string_representation():
    """Test macro string representation"""
    print("\n5. Testing macro string representation...")

    macro1 = Macro("test1", ["scan"], [])
    assert str(macro1) == "test1: scan"

    macro2 = Macro("test2", ["open {url}"], ["url"])
    assert "test2" in str(macro2)
    assert "url" in str(macro2)

    macro3 = Macro("test3", ["cmd {a} {b}"], ["a", "b"])
    assert "test3" in str(macro3)
    assert "a" in str(macro3)
    assert "b" in str(macro3)

    print("   [OK] String representation works")


def test_multiple_commands_expansion():
    """Test that all commands are expanded"""
    print("\n6. Testing multiple commands expansion...")

    mm = MacroManager()
    mm.define(
        "complex",
        ["open {domain}", "scan", "add input where type='{type}'", "list"],
        ["domain", "type"]
    )

    commands = mm.run("complex", ["https://example.com", "email"])
    assert len(commands) == 4
    assert commands[0] == "open https://example.com"
    assert commands[1] == "scan"
    assert commands[2] == "add input where type='email'"
    assert commands[3] == "list"

    print("   [OK] All commands expanded correctly")


def run_all_tests():
    """Run all macro tests"""
    print("="*70)
    print("Parameterised Macro Tests")
    print("="*70)

    tests = [
        test_basic_macro,
        test_macro_with_single_param,
        test_macro_with_multiple_params,
        test_parameter_validation,
        test_macro_string_representation,
        test_multiple_commands_expansion,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result is None or result is True:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n   [FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("="*70)

    if failed == 0:
        print("\n[SUCCESS] All macro parameterization tests passed!")
        return True
    else:
        print(f"\n[ERROR] {failed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
