"""
Test XPath generation
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.core.element import Element


def test_xpath_in_element():
    """Test that Element can store xpath"""
    print("\n" + "="*60)
    print("Testing XPath in Element")
    print("="*60)

    elem = Element(
        index=0,
        uuid="test-uuid",
        tag="input",
        type="email",
        id="email",
        name="user_email",
        selector='input[type="email"]',
        xpath='//*[@id="email"]'
    )

    print(f"\nElement xpath: {elem.xpath}")
    assert elem.xpath == '//*[@id="email"]', "XPath should be stored"
    print("  [OK] Element stores xpath correctly")

    # Test serialization
    elem_dict = elem.to_dict()
    print(f"\nSerialized xpath: {elem_dict.get('xpath')}")
    assert elem_dict.get('xpath') == '//*[@id="email"]', "XPath should be in dict"
    print("  [OK] XPath serialized correctly")

    # Test deserialization
    restored = Element.from_dict(elem_dict)
    print(f"\nRestored xpath: {restored.xpath}")
    assert restored.xpath == '//*[@id="email"]', "XPath should be restored"
    print("  [OK] XPath deserialized correctly")

    print("\n[OK] XPath storage test passed")
    return True


if __name__ == '__main__':
    success = test_xpath_in_element()

    if success:
        print("\n" + "="*60)
        print("[OK] XPath tests passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[FAIL] Tests failed")
        print("="*60)
        sys.exit(1)
