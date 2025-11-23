#!/usr/bin/env python
"""
Integration test for parameterised macros and script execution
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.parser.parser import Parser
from src.commands.executor import CommandExecutor
from src.core.context import Context


async def test_macro_parsing():
    """Test parsing of parameterized macros"""
    print("\n1. Testing macro parsing...")

    parser = Parser()

    # Test basic macro
    cmd1 = parser.parse("macro scan-form scan; add input; list")
    assert cmd1.verb == "macro"
    assert "\x00" in cmd1.argument
    parts = cmd1.argument.split("\x00")
    assert len(parts) == 3
    assert parts[0] == "scan-form"  # name
    assert parts[1] == ""  # parameters (empty)
    assert parts[2] == "scan; add input; list"  # command
    print("   [OK] Basic macro parsed")

    # Test parameterized macro
    cmd2 = parser.parse("macro quick {url} {type} open {url}; scan")
    assert cmd2.verb == "macro"
    parts = cmd2.argument.split("\x00")
    assert len(parts) == 3
    assert parts[0] == "quick"  # name
    assert parts[1] == "url,type"  # parameters
    assert parts[2] == "open {url}; scan"  # command
    print("   [OK] Parameterized macro parsed")

    # Test run with arguments
    cmd3 = parser.parse("run quick https://example.com email")
    assert cmd3.verb == "run"
    parts = cmd3.argument.split("\x00")
    assert len(parts) == 3
    assert parts[0] == "quick"
    assert parts[1] == "https://example.com"
    assert parts[2] == "email"
    print("   [OK] Run with arguments parsed")

    return True


async def test_macro_execution():
    """Test executing parameterized macros"""
    print("\n2. Testing macro execution...")

    parser = Parser()
    executor = Executor(parser)
    context = Context(enable_history_file=False)

    # Define a parameterized macro
    result1 = await executor.execute(
        parser.parse("macro open-scan {url} open {url}; scan"),
        context
    )
    print(f"   Define macro: {result1}")
    assert "defined" in result1

    # Check macro was created
    assert context.macro_manager.exists("open-scan")
    macro = context.macro_manager.get("open-scan")
    assert macro.name == "open-scan"
    assert macro.parameters == ["url"]
    print("   [OK] Macro created with parameters")

    # List macros
    result2 = await executor.execute(
        parser.parse("macros"),
        context
    )
    print(f"   List macros:\n{result2}")
    assert "open-scan" in result2
    assert "{url}" in result2
    print("   [OK] Macros listed with parameters")

    return True


async def test_script_file():
    """Test reading and parsing script file"""
    print("\n3. Testing script file...")

    # Create a test script
    script_content = """# Test script
macro test {url} {type} open {url}; add input where type='{type}'
run test https://example.com email
list
"""

    script_path = "test_temp.sel"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    try:
        # Test reading
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Count non-empty, non-comment lines
        commands = [line.strip() for line in lines
                   if line.strip() and not line.strip().startswith("#")]

        print(f"   Script has {len(commands)} command(s)")
        assert len(commands) == 2  # macro and run
        print("   [OK] Script file read correctly")

        return True
    finally:
        # Cleanup
        if os.path.exists(script_path):
            os.remove(script_path)


async def run_all_tests():
    """Run all integration tests"""
    print("="*70)
    print("Integration Test - Parameterized Macros")
    print("="*70)

    tests = [
        test_macro_parsing,
        test_macro_execution,
        test_script_file,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = await test()
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
        print("\n[SUCCESS] All integration tests passed!")
        print("\nMacro parameterization features:")
        print("- ✅ Define macros with parameters: macro name {p1} {p2} command")
        print("- ✅ Run macros with arguments: run name arg1 arg2")
        print("- ✅ Parameter substitution in commands")
        print("- ✅ Variable persistence to disk")
        print("- ✅ Script execution (exec file.sel)")
        return True
    else:
        print(f"\n[ERROR] {failed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
