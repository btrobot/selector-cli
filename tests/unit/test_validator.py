#!/usr/bin/env python
"""
Phase 4 - Comprehensive Validator Tests
Test coverage for UniquenessValidator - all 3 levels
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.validator import UniquenessValidator
from src.core.element import Element


# Mock Page classes
class MockLocator:
    """Mock Playwright Locator"""

    def __init__(self, elements=None, count_value=None, evaluate_result=None, attrs=None):
        self.elements = elements or []
        self.count_value = count_value
        self.evaluate_result = evaluate_result or "input"

        # Always set these attributes for email-related elements
        if self.evaluate_result == "input":
            self.attrs = {
                'type': 'email',
                'name': 'email-input',
                'id': 'email-field'
            }
        else:
            self.attrs = attrs or {}

    async def count(self):
        return self.count_value if self.count_value is not None else len(self.elements)

    def first(self):
        return self

    async def evaluate(self, script):
        return self.evaluate_result

    async def get_attribute(self, name):
        # Always return the attribute from attrs dict
        return self.attrs.get(name) if hasattr(self, 'attrs') else None


class MockPage:
    """Mock Playwright Page"""

    def __init__(self, url="https://example.com"):
        self.url = url
        self.locator_calls = []

    def locator(self, selector):
        self.locator_calls.append(selector)

        # Fix: Always return input for email-field selector
        if "email-field" in selector or "#email" in selector:
            return MockLocator(count_value=1, evaluate_result="input")
        elif selector in ["#unique-id", "xpath=//div[@id='unique']"]:
            return MockLocator(count_value=1, evaluate_result="div")
        elif selector in [".multiple", "xpath=//button"]:
            return MockLocator(count_value=5, evaluate_result="button")
        elif selector == "#non-existent":
            return MockLocator(count_value=0)
        elif "@id='wrong-id'" in selector or "#wrong-id" in selector:
            return MockLocator(count_value=1, evaluate_result="div")
        else:
            return MockLocator(count_value=1)


# Test Element fixtures
def create_element(**kwargs):
    """Create test element with default values"""
    defaults = {
        'index': 0,
        'uuid': 'test-uuid',
        'tag': 'input',
        'type': 'email',
        'id': 'email-field',
        'name': 'email-input',
        'placeholder': 'Email',
        'text': '',
        'classes': [],
        'attributes': {}
    }
    defaults.update(kwargs)
    return Element(**defaults)


async def test_is_unique_success():
    """Test is_unique with unique selector"""
    print("\n1. Testing is_unique() with unique selector...")

    validator = UniquenessValidator()
    page = MockPage()

    result = await validator.is_unique("#unique-id", page, is_xpath=False)

    assert result is True, f"Expected True, got {result}"
    print("   [OK] Unique selector validated successfully")
    return True


async def test_is_unique_non_unique():
    """Test is_unique with non-unique selector"""
    print("\n2. Testing is_unique() with non-unique selector...")

    validator = UniquenessValidator()
    page = MockPage()

    result = await validator.is_unique(".multiple", page, is_xpath=False)

    assert result is False, f"Expected False, got {result}"
    print("   [OK] Non-unique selector correctly rejected")
    return True


async def test_is_unique_xpath():
    """Test is_unique with XPath selector"""
    print("\n3. Testing is_unique() with XPath...")

    validator = UniquenessValidator()
    page = MockPage()

    result = await validator.is_unique("//div[@id='unique']", page, is_xpath=True)

    assert result is True, f"Expected True, got {result}"
    print("   [OK] XPath selector validated successfully")
    return True


async def test_is_unique_cache():
    """Test cache functionality"""
    print("\n4. Testing validation cache...")

    validator = UniquenessValidator()
    page = MockPage()

    # First call
    result1 = await validator.is_unique("#unique-id", page, is_xpath=False)

    # Second call (should use cache, no additional locator calls)
    initial_calls = len(page.locator_calls)
    result2 = await validator.is_unique("#unique-id", page, is_xpath=False)
    final_calls = len(page.locator_calls)

    assert result1 == result2, "Cache returned different result"
    assert final_calls == initial_calls, "Cache was not used"
    print("   [OK] Cache functionality working")
    return True


async def test_matches_target_success():
    """Test matches_target with matching element"""
    print("\n5. Testing matches_target() with matching element...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element(tag="input", type="email", id="email-field")

    # Debug: Check what we're sending
    print(f"    [DEBUG] Element: tag={element.tag}, type={element.type}, id={element.id}")

    result = await validator.matches_target("#email-field", element, page, is_xpath=False)

    # Debug: Check what we got
    print(f"    [DEBUG] Result: {result}")

    assert result is True, f"Expected True, got {result}"
    print("   [OK] Matching target correctly identified")
    return True


async def test_matches_target_wrong_tag():
    """Test matches_target with wrong tag"""
    print("\n6. Testing matches_target() with wrong tag...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element(tag="input", type="email")

    result = await validator.matches_target("#wrong-id", element, page, is_xpath=False)

    assert result is False, f"Expected False, got {result}"
    print("   [OK] Wrong tag correctly rejected")
    return True


async def test_is_strictly_unique():
    """Test is_strictly_unique combining all levels"""
    print("\n7. Testing is_strictly_unique()...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element(tag="input", type="email", id="email-field")

    result = await validator.is_strictly_unique("#email-field", element, page, is_xpath=False)

    assert result is True, f"Expected True, got {result}"
    print("   [OK] Strictly unique element confirmed")
    return True


async def test_is_strictly_unique_not_unique():
    """Test is_strictly_unique with non-unique selector"""
    print("\n8. Testing is_strictly_unique() with non-unique selector...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element()

    result = await validator.is_strictly_unique(".multiple", element, page, is_xpath=False)

    assert result is False, f"Expected False, got {result}"
    print("   [OK] Non-unique correctly rejected at Level 1")
    return True


async def test_validate_selector_quality_valid():
    """Test validate_selector_quality with valid selector"""
    print("\n9. Testing validate_selector_quality() with valid selector...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element(tag="input", type="email", id="email-field")

    result = await validator.validate_selector_quality("#email-field", element, page, is_xpath=False)

    assert result['is_valid'] is True, f"Expected valid=True, got {result['is_valid']}"
    assert result['level1_unique'] is True
    assert result['level2_matches_target'] is True
    assert result['quality_score'] == 1.0
    print("   [OK] Quality validation passed for valid selector")
    return True


async def test_validate_selector_quality_not_unique():
    """Test validate_selector_quality with non-unique selector"""
    print("\n10. Testing validate_selector_quality() with non-unique selector...")

    validator = UniquenessValidator()
    page = MockPage()
    element = create_element()

    result = await validator.validate_selector_quality(".multiple", element, page, is_xpath=False)

    assert result['is_valid'] is False, f"Expected valid=False, got {result['is_valid']}"
    assert result['level1_unique'] is False
    assert result['quality_score'] < 1.0
    assert len(result['issues']) > 0, "Should have issues reported"
    print("   [OK] Quality validation correctly identified issues")
    return True


async def test_clear_cache():
    """Test cache clearing"""
    print("\n11. Testing cache clear functionality...")

    validator = UniquenessValidator()
    page = MockPage()

    # Add to cache
    await validator.is_unique("#unique-id", page)
    cache_size = len(validator.validation_cache)

    assert cache_size > 0, "Cache should have entries"

    # Clear cache
    validator.clear_cache()

    assert len(validator.validation_cache) == 0, "Cache should be empty"
    print("   [OK] Cache clear working")
    return True


async def test_cache_stats():
    """Test cache statistics"""
    print("\n12. Testing cache stats...")

    validator = UniquenessValidator()
    page = MockPage()

    # Add entries
    await validator.is_unique("#test1", page)
    await validator.is_unique("#test2", page)

    stats = validator.cache_stats()

    assert stats['cache_size'] == 2, f"Expected cache size 2, got {stats['cache_size']}"
    assert len(stats['cache_keys']) > 0, "Should have cache keys"
    print("   [OK] Cache stats working")
    return True


async def test_exception_handling():
    """Test exception handling in validation"""
    print("\n13. Testing exception handling...")

    validator = UniquenessValidator()
    element = create_element()

    # Create a mock page that raises exceptions
    class ExceptionPage:
        url = "https://example.com"
        def locator(self, selector):
            raise Exception("Simulated error")

    page = ExceptionPage()

    # Should handle exception gracefully
    result = await validator.is_unique("#test", page)
    assert result is False, f"Expected False on exception, got {result}"

    target_result = await validator.matches_target("#test", element, page)
    assert target_result is False, f"Expected False on exception, got {target_result}"

    print("   [OK] Exception handling working")
    return True


async def run_all_tests():
    """Run all validator tests"""
    print("="*60)
    print("Phase 4 - Validator Comprehensive Tests")
    print("="*60)

    all_tests = [
        test_is_unique_success,
        test_is_unique_non_unique,
        test_is_unique_xpath,
        test_is_unique_cache,
        test_matches_target_success,
        test_matches_target_wrong_tag,
        test_is_strictly_unique,
        test_is_strictly_unique_not_unique,
        test_validate_selector_quality_valid,
        test_validate_selector_quality_not_unique,
        test_clear_cache,
        test_cache_stats,
        test_exception_handling,
    ]

    passed = 0
    failed = 0

    for test in all_tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   [FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n[PASS] ALL VALIDATOR TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
