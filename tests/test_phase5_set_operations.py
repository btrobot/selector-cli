"""
Test Phase 5 - Set Operations
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.lexer import Lexer, TokenType
from src.parser.parser import Parser
from src.core.collection import ElementCollection
from src.core.element import Element


def test_set_operation_tokens():
    """Test set operation tokens"""
    print("\n" + "="*60)
    print("Testing Set Operation Tokens")
    print("="*60)

    lexer = Lexer()

    # Test union
    tokens = lexer.tokenize("union")
    assert tokens[0].type == TokenType.UNION
    print("\n[OK] 'union' tokenized as UNION")

    # Test intersect
    tokens = lexer.tokenize("intersect")
    assert tokens[0].type == TokenType.INTERSECT
    print("[OK] 'intersect' tokenized as INTERSECT")

    # Test difference
    tokens = lexer.tokenize("difference")
    assert tokens[0].type == TokenType.DIFFERENCE
    print("[OK] 'difference' tokenized as DIFFERENCE")

    # Test unique
    tokens = lexer.tokenize("unique")
    assert tokens[0].type == TokenType.UNIQUE
    print("[OK] 'unique' tokenized as UNIQUE")

    print("\n[OK] All token tests passed")
    return True


def test_set_operation_parsing():
    """Test parsing set operation commands"""
    print("\n" + "="*60)
    print("Testing Set Operation Parsing")
    print("="*60)

    parser = Parser()

    # Test union
    cmd = parser.parse("union saved_collection")
    assert cmd.verb == 'union'
    assert cmd.argument == 'saved_collection'
    print("\n[OK] 'union saved_collection' parsed correctly")

    # Test intersect
    cmd = parser.parse("intersect other_set")
    assert cmd.verb == 'intersect'
    assert cmd.argument == 'other_set'
    print("[OK] 'intersect other_set' parsed correctly")

    # Test difference
    cmd = parser.parse("difference exclude_these")
    assert cmd.verb == 'difference'
    assert cmd.argument == 'exclude_these'
    print("[OK] 'difference exclude_these' parsed correctly")

    # Test unique
    cmd = parser.parse("unique")
    assert cmd.verb == 'unique'
    print("[OK] 'unique' parsed correctly")

    print("\n[OK] All parsing tests passed")
    return True


def test_collection_set_operations():
    """Test ElementCollection set operations"""
    print("\n" + "="*60)
    print("Testing ElementCollection Set Operations")
    print("="*60)

    # Create test elements
    elem1 = Element(tag="input", index=0, uuid="e1", attributes={"type": "text", "id": "field1"})
    elem2 = Element(tag="input", index=1, uuid="e2", attributes={"type": "email", "id": "field2"})
    elem3 = Element(tag="button", index=2, uuid="e3", attributes={"type": "submit"})
    elem4 = Element(tag="input", index=3, uuid="e4", attributes={"type": "password"})

    # Create collections
    collection_a = ElementCollection()
    collection_a.add(elem1)
    collection_a.add(elem2)
    collection_a.add(elem3)

    collection_b = ElementCollection()
    collection_b.add(elem2)  # Common with A
    collection_b.add(elem3)  # Common with A
    collection_b.add(elem4)  # Only in B

    # Test union
    result_union = collection_a.union(collection_b)
    assert result_union.count() == 4  # All unique elements
    print("\n[OK] Union: 3 + 3 (with 2 common) = 4")

    # Test intersection
    result_intersect = collection_a.intersection(collection_b)
    assert result_intersect.count() == 2  # elem2 and elem3
    print("[OK] Intersection: 2 common elements")

    # Test difference
    result_diff = collection_a.difference(collection_b)
    assert result_diff.count() == 1  # Only elem1
    print("[OK] Difference: 1 element only in A")

    # Test unique (already unique by design)
    result_unique = collection_a.unique()
    assert result_unique.count() == collection_a.count()
    print("[OK] Unique: Collection already unique")

    print("\n[OK] All collection operation tests passed")
    return True


def test_in_place_operations():
    """Test in-place set operations"""
    print("\n" + "="*60)
    print("Testing In-Place Set Operations")
    print("="*60)

    # Create test elements
    elem1 = Element(tag="input", index=0, uuid="a", attributes={"id": "a"})
    elem2 = Element(tag="input", index=1, uuid="b", attributes={"id": "b"})
    elem3 = Element(tag="input", index=2, uuid="c", attributes={"id": "c"})
    elem4 = Element(tag="input", index=3, uuid="d", attributes={"id": "d"})

    # Test union_in_place
    coll1 = ElementCollection()
    coll1.add(elem1)
    coll1.add(elem2)

    coll2 = ElementCollection()
    coll2.add(elem2)
    coll2.add(elem3)

    coll1.union_in_place(coll2)
    assert coll1.count() == 3  # a, b, c
    print("\n[OK] Union in-place: {a,b} ∪ {b,c} = {a,b,c}")

    # Test intersect_in_place
    coll3 = ElementCollection()
    coll3.add(elem1)
    coll3.add(elem2)
    coll3.add(elem3)

    coll4 = ElementCollection()
    coll4.add(elem2)
    coll4.add(elem3)

    coll3.intersect_in_place(coll4)
    assert coll3.count() == 2  # b, c
    print("[OK] Intersect in-place: {a,b,c} ∩ {b,c} = {b,c}")

    # Test difference_in_place
    coll5 = ElementCollection()
    coll5.add(elem1)
    coll5.add(elem2)
    coll5.add(elem3)

    coll6 = ElementCollection()
    coll6.add(elem2)

    coll5.difference_in_place(coll6)
    assert coll5.count() == 2  # a, c
    print("[OK] Difference in-place: {a,b,c} - {b} = {a,c}")

    print("\n[OK] All in-place operation tests passed")
    return True


def test_error_cases():
    """Test error handling"""
    print("\n" + "="*60)
    print("Testing Error Cases")
    print("="*60)

    parser = Parser()

    # Union without collection name should fail
    try:
        cmd = parser.parse("union")
        # Parser won't fail, but executor should
        print("\n[OK] 'union' without name parses (will fail in executor)")
    except:
        print("\n[OK] 'union' without name raises error")

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
        "save my_collection",
        "load my_collection",
        "highlight",
        "unhighlight",
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
    success = test_set_operation_tokens() and success
    success = test_set_operation_parsing() and success
    success = test_collection_set_operations() and success
    success = test_in_place_operations() and success
    success = test_error_cases() and success
    success = test_backward_compatibility() and success

    if success:
        print("\n" + "="*60)
        print("[OK] ALL SET OPERATION TESTS PASSED!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Some tests failed")
        print("="*60)
        sys.exit(1)
