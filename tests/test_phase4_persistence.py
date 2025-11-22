"""
Test Phase 4 - Persistence and Variables
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.parser import Parser
from src.core.storage import StorageManager
from src.core.element import Element


def create_test_elements():
    """Create test elements"""
    return [
        Element(
            index=0,
            uuid="elem-0",
            tag="input",
            selector='input[type="email"]',
            type="email",
            id="email",
            name="user_email",
            placeholder="Enter email",
            text="",
            attributes={"type": "email", "id": "email"}
        ),
        Element(
            index=1,
            uuid="elem-1",
            tag="button",
            selector='button[type="submit"]',
            type="submit",
            id="submit-btn",
            name="",
            placeholder="",
            text="Login",
            attributes={"type": "submit", "id": "submit-btn"}
        ),
    ]


def test_parser_persistence_commands():
    """Test parsing of persistence commands"""
    print("\n" + "="*60)
    print("Testing Persistence Command Parsing")
    print("="*60)

    parser = Parser()

    tests = [
        ("save login_form", "save", "login_form"),
        ("save 'my collection'", "save", "my collection"),
        ("load login_form", "load", "login_form"),
        ("load 'my collection'", "load", "my collection"),
        ("saved", "saved", None),
        ("delete login_form", "delete", "login_form"),
        ("set timeout = 30", "set", "timeout=30"),
        ("set name = 'test'", "set", "name=test"),
        ("vars", "vars", None),
    ]

    for test_input, expected_verb, expected_arg in tests:
        print(f"\nInput: {test_input}")
        cmd = parser.parse(test_input)

        assert cmd.verb == expected_verb, f"Expected verb '{expected_verb}', got {cmd.verb}"
        if expected_arg is not None:
            assert cmd.argument == expected_arg, f"Expected argument '{expected_arg}', got {cmd.argument}"
        print(f"  [OK] verb={cmd.verb}, argument={cmd.argument}")

    print("\n[OK] Persistence command parsing tests passed")
    return True


def test_storage_manager():
    """Test storage manager functionality"""
    print("\n" + "="*60)
    print("Testing Storage Manager")
    print("="*60)

    # Use temp directory for tests
    temp_dir = tempfile.mkdtemp()

    try:
        storage = StorageManager(storage_dir=temp_dir)
        elements = create_test_elements()

        # Test save
        print("\nTest: save_collection")
        filepath = storage.save_collection("test_coll", elements, "https://example.com")
        assert os.path.exists(filepath), "File should exist"
        print(f"  [OK] Saved to {filepath}")

        # Test exists
        print("\nTest: collection_exists")
        assert storage.collection_exists("test_coll"), "Collection should exist"
        assert not storage.collection_exists("nonexistent"), "Nonexistent should not exist"
        print("  [OK] collection_exists works")

        # Test list
        print("\nTest: list_collections")
        collections = storage.list_collections()
        assert len(collections) == 1, f"Expected 1 collection, got {len(collections)}"
        assert collections[0]["name"] == "test_coll"
        assert collections[0]["count"] == 2
        print(f"  [OK] Listed {len(collections)} collection(s)")

        # Test load
        print("\nTest: load_collection")
        loaded_elements, metadata = storage.load_collection("test_coll")
        assert len(loaded_elements) == 2, f"Expected 2 elements, got {len(loaded_elements)}"
        assert loaded_elements[0].tag == "input"
        assert loaded_elements[1].tag == "button"
        assert metadata["url"] == "https://example.com"
        print(f"  [OK] Loaded {len(loaded_elements)} element(s)")

        # Test delete
        print("\nTest: delete_collection")
        storage.delete_collection("test_coll")
        assert not storage.collection_exists("test_coll"), "Collection should be deleted"
        print("  [OK] Collection deleted")

        # Test load nonexistent
        print("\nTest: load nonexistent collection")
        try:
            storage.load_collection("nonexistent")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            print("  [OK] Correctly raises FileNotFoundError")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

    print("\n[OK] Storage manager tests passed")
    return True


def test_storage_sanitize_name():
    """Test filename sanitization"""
    print("\n" + "="*60)
    print("Testing Filename Sanitization")
    print("="*60)

    temp_dir = tempfile.mkdtemp()

    try:
        storage = StorageManager(storage_dir=temp_dir)

        # Test with special characters
        result = storage._sanitize_name("test<>name")
        assert "<" not in result and ">" not in result
        print(f"  [OK] 'test<>name' -> '{result}'")

        result = storage._sanitize_name("path/to/file")
        assert "/" not in result
        print(f"  [OK] 'path/to/file' -> '{result}'")

    finally:
        shutil.rmtree(temp_dir)

    print("\n[OK] Filename sanitization tests passed")
    return True


def test_element_serialization():
    """Test element to/from dict conversion"""
    print("\n" + "="*60)
    print("Testing Element Serialization")
    print("="*60)

    temp_dir = tempfile.mkdtemp()

    try:
        storage = StorageManager(storage_dir=temp_dir)
        original = create_test_elements()[0]

        # Convert to dict and back
        as_dict = storage._element_to_dict(original)
        restored = storage._dict_to_element(as_dict)

        # Verify fields
        assert restored.index == original.index
        assert restored.tag == original.tag
        assert restored.type == original.type
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.selector == original.selector
        assert restored.placeholder == original.placeholder
        assert restored.visible == original.visible
        assert restored.enabled == original.enabled

        print("  [OK] Element fields preserved after serialization")

    finally:
        shutil.rmtree(temp_dir)

    print("\n[OK] Element serialization tests passed")
    return True


def test_multiple_collections():
    """Test managing multiple collections"""
    print("\n" + "="*60)
    print("Testing Multiple Collections")
    print("="*60)

    temp_dir = tempfile.mkdtemp()

    try:
        storage = StorageManager(storage_dir=temp_dir)
        elements = create_test_elements()

        # Save multiple collections
        storage.save_collection("coll1", elements, "https://site1.com")
        storage.save_collection("coll2", elements[:1], "https://site2.com")
        storage.save_collection("coll3", elements, "https://site3.com")

        # List and verify
        collections = storage.list_collections()
        assert len(collections) == 3, f"Expected 3, got {len(collections)}"

        names = [c["name"] for c in collections]
        assert "coll1" in names
        assert "coll2" in names
        assert "coll3" in names

        print(f"  [OK] Created and listed {len(collections)} collections")

        # Delete one
        storage.delete_collection("coll2")
        collections = storage.list_collections()
        assert len(collections) == 2

        print("  [OK] Deleted one, remaining: 2")

    finally:
        shutil.rmtree(temp_dir)

    print("\n[OK] Multiple collections tests passed")
    return True


if __name__ == '__main__':
    success = True
    success = test_parser_persistence_commands() and success
    success = test_storage_manager() and success
    success = test_storage_sanitize_name() and success
    success = test_element_serialization() and success
    success = test_multiple_collections() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL PHASE 4 TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
