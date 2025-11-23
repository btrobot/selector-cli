"""
Test Phase 5 - Auto-completion
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.core.completer import SelectorCompleter
from src.core.context import Context
from src.core.storage import StorageManager


def test_command_completion():
    """Test command completion"""
    print("\n" + "="*60)
    print("Testing Command Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test completing commands from empty
    matches = completer._match('', completer.COMMANDS)
    assert len(matches) > 0
    assert 'add' in matches
    assert 'open' in matches
    print(f"\n[OK] Empty text returns {len(matches)} commands")

    # Test completing 'ad' -> 'add'
    matches = completer._match('ad', completer.COMMANDS)
    assert 'add' in matches
    print("[OK] 'ad' completes to 'add'")

    # Test completing 'hi' -> 'highlight'
    matches = completer._match('hi', completer.COMMANDS)
    assert 'highlight' in matches
    print("[OK] 'hi' completes to 'highlight'")

    # Test completing 'un' -> 'union', 'unique', 'unhighlight'
    matches = completer._match('un', completer.COMMANDS)
    assert 'union' in matches
    assert 'unique' in matches
    assert 'unhighlight' in matches
    print(f"[OK] 'un' completes to {len(matches)} commands: {matches}")

    print("\n[OK] All command completion tests passed")
    return True


def test_element_type_completion():
    """Test element type completion"""
    print("\n" + "="*60)
    print("Testing Element Type Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test element types
    matches = completer._match('', completer.ELEMENT_TYPES)
    assert 'input' in matches
    assert 'button' in matches
    assert 'select' in matches
    print(f"\n[OK] Found {len(matches)} element types")

    # Test completing 'in' -> 'input'
    matches = completer._match('in', completer.ELEMENT_TYPES)
    assert 'input' in matches
    print("[OK] 'in' completes to 'input'")

    # Test completing 'bu' -> 'button'
    matches = completer._match('bu', completer.ELEMENT_TYPES)
    assert 'button' in matches
    print("[OK] 'bu' completes to 'button'")

    print("\n[OK] All element type completion tests passed")
    return True


def test_field_completion():
    """Test field name completion"""
    print("\n" + "="*60)
    print("Testing Field Name Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test field names
    matches = completer._match('', completer.FIELDS)
    assert 'type' in matches
    assert 'id' in matches
    assert 'name' in matches
    print(f"\n[OK] Found {len(matches)} field names")

    # Test completing 'ty' -> 'type'
    matches = completer._match('ty', completer.FIELDS)
    assert 'type' in matches
    print("[OK] 'ty' completes to 'type'")

    # Test completing 'vis' -> 'visible'
    matches = completer._match('vis', completer.FIELDS)
    assert 'visible' in matches
    print("[OK] 'vis' completes to 'visible'")

    print("\n[OK] All field name completion tests passed")
    return True


def test_export_format_completion():
    """Test export format completion"""
    print("\n" + "="*60)
    print("Testing Export Format Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test completing 'pla' -> 'playwright'
    matches = completer._match('pla', completer.EXPORT_FORMATS)
    assert 'playwright' in matches
    print("\n[OK] 'pla' completes to 'playwright'")

    # Test completing 'sel' -> 'selenium'
    matches = completer._match('sel', completer.EXPORT_FORMATS)
    assert 'selenium' in matches
    print("[OK] 'sel' completes to 'selenium'")

    # Test completing 'j' -> 'json'
    matches = completer._match('j', completer.EXPORT_FORMATS)
    assert 'json' in matches
    print("[OK] 'j' completes to 'json'")

    print("\n[OK] All export format completion tests passed")
    return True


def test_context_aware_completion():
    """Test context-aware completion"""
    print("\n" + "="*60)
    print("Testing Context-Aware Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test 'add' command - should complete element types
    matches = completer._complete_add_remove(['add'], 'in')
    assert 'input' in matches
    print("\n[OK] After 'add', 'in' completes to 'input'")

    # Test 'add input' - should complete 'where'
    matches = completer._complete_add_remove(['add', 'input'], 'wh')
    assert 'where' in matches
    print("[OK] After 'add input', 'wh' completes to 'where'")

    # Test 'add input where' - should complete field names
    matches = completer._complete_add_remove(['add', 'input', 'where'], 'ty')
    assert 'type' in matches
    print("[OK] After 'add input where', 'ty' completes to 'type'")

    # Test 'add input where type' - should complete operators
    matches = completer._complete_add_remove(['add', 'input', 'where', 'type'], 'con')
    assert 'contains' in matches
    print("[OK] After 'add input where type', 'con' completes to 'contains'")

    print("\n[OK] All context-aware completion tests passed")
    return True


def test_collection_name_completion():
    """Test collection name completion"""
    print("\n" + "="*60)
    print("Testing Collection Name Completion")
    print("="*60)

    # Create storage with temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageManager(tmpdir)
        completer = SelectorCompleter(storage=storage)

        # Initially no collections
        matches = completer._complete_collection_name(['load'], '')
        assert len(matches) == 0
        print("\n[OK] No collections initially")

        # Create some mock collections
        from src.core.collection import ElementCollection
        from src.core.element import Element

        elem = Element(tag="input", index=0, uuid="test")
        coll = ElementCollection()
        coll.add(elem)

        storage.save_collection('test_inputs', coll)
        storage.save_collection('test_buttons', coll)
        storage.save_collection('prod_data', coll)

        # Test completion
        matches = completer._complete_collection_name(['load'], 'test')
        assert 'test_inputs' in matches
        assert 'test_buttons' in matches
        assert 'prod_data' not in matches
        print(f"[OK] 'test' completes to {len(matches)} collections")

        # Test all
        matches = completer._complete_collection_name(['load'], '')
        assert len(matches) == 3
        print(f"[OK] Empty text returns all {len(matches)} collections")

    print("\n[OK] All collection name completion tests passed")
    return True


def test_match_function():
    """Test _match helper function"""
    print("\n" + "="*60)
    print("Testing _match Function")
    print("="*60)

    completer = SelectorCompleter()

    options = ['apple', 'apricot', 'banana', 'cherry', 'avocado']

    # Test exact prefix match
    matches = completer._match('ap', options)
    assert matches == ['apple', 'apricot']
    print("\n[OK] 'ap' matches ['apple', 'apricot']")

    # Test single character
    matches = completer._match('a', options)
    assert matches == ['apple', 'apricot', 'avocado']
    print("[OK] 'a' matches ['apple', 'apricot', 'avocado']")

    # Test no matches
    matches = completer._match('z', options)
    assert matches == []
    print("[OK] 'z' matches nothing")

    # Test empty text (returns all)
    matches = completer._match('', options)
    assert len(matches) == 5
    print(f"[OK] Empty text returns all {len(matches)} options")

    print("\n[OK] All _match function tests passed")
    return True


def test_string_operator_completion():
    """Test string operator completion"""
    print("\n" + "="*60)
    print("Testing String Operator Completion")
    print("="*60)

    completer = SelectorCompleter()

    # Test completing 'con' -> 'contains'
    matches = completer._match('con', completer.STRING_OPS)
    assert 'contains' in matches
    print("\n[OK] 'con' completes to 'contains'")

    # Test completing 's' -> 'starts'
    matches = completer._match('s', completer.STRING_OPS)
    assert 'starts' in matches
    print("[OK] 's' completes to 'starts'")

    # Test completing 'm' -> 'matches'
    matches = completer._match('m', completer.STRING_OPS)
    assert 'matches' in matches
    print("[OK] 'm' completes to 'matches'")

    print("\n[OK] All string operator completion tests passed")
    return True


if __name__ == '__main__':
    success = True
    success = test_command_completion() and success
    success = test_element_type_completion() and success
    success = test_field_completion() and success
    success = test_export_format_completion() and success
    success = test_context_aware_completion() and success
    success = test_collection_name_completion() and success
    success = test_match_function() and success
    success = test_string_operator_completion() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL AUTO-COMPLETION TESTS PASSED!")
        print("="*60)
        print("\nNote: These tests verify the completer logic.")
        print("Interactive Tab completion requires running the REPL.")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
