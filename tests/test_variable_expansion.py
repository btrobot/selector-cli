"""
Test Variable Expansion
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.core.variable_expander import VariableExpander


def test_simple_variable_expansion():
    """Test simple $var expansion"""
    print("\n" + "="*60)
    print("Testing Simple Variable Expansion")
    print("="*60)

    expander = VariableExpander()
    variables = {
        "url": "https://example.com",
        "timeout": 30,
        "base_path": "/api/v1"
    }

    tests = [
        ("open $url", "open https://example.com"),
        ("set timeout = $timeout", "set timeout = 30"),
        ("export json > $base_path/data.json", "export json > /api/v1/data.json"),
    ]

    for input_text, expected in tests:
        print(f"\nInput: {input_text}")
        result = expander.expand(input_text, variables)
        print(f"Output: {result}")
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("  [OK]")

    print("\n[OK] Simple variable expansion tests passed")
    return True


def test_braced_variable_expansion():
    """Test ${var} expansion with explicit boundary"""
    print("\n" + "="*60)
    print("Testing Braced Variable Expansion")
    print("="*60)

    expander = VariableExpander()
    variables = {
        "protocol": "https",
        "domain": "example.com",
        "port": "8080"
    }

    tests = [
        ("open ${protocol}://${domain}", "open https://example.com"),
        ("open ${protocol}://${domain}:${port}", "open https://example.com:8080"),
        ("set url = ${protocol}://${domain}/login", "set url = https://example.com/login"),
    ]

    for input_text, expected in tests:
        print(f"\nInput: {input_text}")
        result = expander.expand(input_text, variables)
        print(f"Output: {result}")
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("  [OK]")

    print("\n[OK] Braced variable expansion tests passed")
    return True


def test_mixed_variable_expansion():
    """Test mixed $var and ${var} expansion"""
    print("\n" + "="*60)
    print("Testing Mixed Variable Expansion")
    print("="*60)

    expander = VariableExpander()
    variables = {
        "base": "https://example.com",
        "path": "/api",
        "version": "v1"
    }

    tests = [
        ("open $base${path}/$version", "open https://example.com/api/v1"),
        ("set url = $base${path}", "set url = https://example.com/api"),
    ]

    for input_text, expected in tests:
        print(f"\nInput: {input_text}")
        result = expander.expand(input_text, variables)
        print(f"Output: {result}")
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("  [OK]")

    print("\n[OK] Mixed variable expansion tests passed")
    return True


def test_undefined_variable_error():
    """Test error on undefined variable"""
    print("\n" + "="*60)
    print("Testing Undefined Variable Error")
    print("="*60)

    expander = VariableExpander()
    variables = {"defined": "value"}

    try:
        result = expander.expand("open $undefined", variables)
        assert False, "Should raise ValueError for undefined variable"
    except ValueError as e:
        print(f"\n[OK] Correctly raised error: {e}")

    try:
        result = expander.expand("open ${undefined}", variables)
        assert False, "Should raise ValueError for undefined variable"
    except ValueError as e:
        print(f"[OK] Correctly raised error for braced: {e}")

    print("\n[OK] Undefined variable error tests passed")
    return True


def test_no_variables():
    """Test text without variables"""
    print("\n" + "="*60)
    print("Testing Text Without Variables")
    print("="*60)

    expander = VariableExpander()
    variables = {"url": "https://example.com"}

    tests = [
        "open https://test.com",
        "add input where type=\"email\"",
        "list",
    ]

    for input_text in tests:
        print(f"\nInput: {input_text}")
        result = expander.expand(input_text, variables)
        print(f"Output: {result}")
        assert result == input_text, "Should return unchanged"
        print("  [OK] Unchanged")

    print("\n[OK] No variables tests passed")
    return True


def test_has_variables():
    """Test variable detection"""
    print("\n" + "="*60)
    print("Testing Variable Detection")
    print("="*60)

    expander = VariableExpander()

    tests = [
        ("open $url", True),
        ("open ${url}", True),
        ("open $url${path}", True),
        ("open https://test.com", False),
        ("list", False),
    ]

    for input_text, expected in tests:
        print(f"\nInput: {input_text}")
        result = expander.has_variables(input_text)
        print(f"Has variables: {result}")
        assert result == expected, f"Expected {expected}, got {result}"
        print("  [OK]")

    print("\n[OK] Variable detection tests passed")
    return True


def test_get_variable_names():
    """Test extracting variable names"""
    print("\n" + "="*60)
    print("Testing Variable Name Extraction")
    print("="*60)

    expander = VariableExpander()

    tests = [
        ("open $url", ["url"]),
        ("open ${protocol}://${domain}", ["protocol", "domain"]),
        ("set x = $a$b${c}", ["a", "b", "c"]),
        ("list", []),
    ]

    for input_text, expected_names in tests:
        print(f"\nInput: {input_text}")
        result = expander.get_variable_names(input_text)
        print(f"Variables: {result}")
        assert set(result) == set(expected_names), f"Expected {expected_names}, got {result}"
        print("  [OK]")

    print("\n[OK] Variable name extraction tests passed")
    return True


if __name__ == '__main__':
    success = True
    success = test_simple_variable_expansion() and success
    success = test_braced_variable_expansion() and success
    success = test_mixed_variable_expansion() and success
    success = test_undefined_variable_error() and success
    success = test_no_variables() and success
    success = test_has_variables() and success
    success = test_get_variable_names() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL VARIABLE EXPANSION TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
