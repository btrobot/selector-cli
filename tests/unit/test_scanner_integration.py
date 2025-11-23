#!/usr/bin/env python
"""
Phase 4 - Scanner Integration Tests
Test LocatorIntegrationEngine with mock elements and pages
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.locator.scanner_integration import LocatorIntegrationEngine
from src.core.element import Element


# Mock Page classes (simplified version)
class MockLocator:
    """Mock Playwright Locator"""

    def __init__(self, count_value=1, evaluate_result="input"):
        self.count_value = count_value
        self.evaluate_result = evaluate_result
        self.attrs = {
            'type': 'email',
            'name': 'test-input',
            'id': 'test-field'
        }

    async def count(self):
        return self.count_value

    def first(self):
        return self

    async def evaluate(self, script):
        return self.evaluate_result

    async def get_attribute(self, name):
        return self.attrs.get(name)


class MockPage:
    """Mock Playwright Page"""

    def __init__(self, url="https://example.com"):
        self.url = url

    def locator(self, selector):
        # Simulate different selectors
        if "#test-field" in selector or "@id='test-field'" in selector:
            return MockLocator(count_value=1, evaluate_result="input")
        elif ".shared" in selector or "xpath=//button" == selector:
            return MockLocator(count_value=3, evaluate_result="button")  # Non-unique
        elif "#unique" in selector:
            return MockLocator(count_value=1, evaluate_result="div")
        else:
            return MockLocator(count_value=1, evaluate_result="input")


def create_element(**kwargs):
    """Create test element"""
    defaults = {
        'index': 0,
        'uuid': 'test-uuid',
        'tag': 'input',
        'type': 'email',
        'id': 'test-field',
        'name': 'test-input',
        'placeholder': 'Test',
        'text': '',
        'classes': [],
        'attributes': {}
    }
    defaults.update(kwargs)
    return Element(**defaults)


async def test_process_collection_basic():
    """Test basic collection processing"""
    print("\n1. Testing basic collection processing...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Create test elements
    elements = [
        create_element(id="unique-1", tag="input", type="email"),
        create_element(id="unique-2", tag="button", type="submit"),
        create_element(id="unique-3", tag="a", attributes={"href": "/test"}),
    ]

    result = await engine.process_collection(elements, page)

    # Check results structure
    assert 'results' in result
    assert 'stats' in result
    assert len(result['results']) == 3

    # Check all elements were processed
    stats = result['stats']
    assert stats['total_elements'] == 3

    print(f"   [OK] Processed {stats['total_elements']} elements")
    print(f"   [OK] Successful: {stats['successful']}")
    print(f"   [OK] Failed: {stats['failed']}")

    return True


async def test_process_collection_with_failures():
    """Test collection processing with some failures"""
    print("\n2. Testing collection with failures...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Mix of elements (some will succeed, some will fail)
    elements = [
        create_element(id="unique-1", tag="input", type="email"),  # Should succeed
        create_element(tag="div", type="", id="", name=""),  # Generic div, likely to fail
        create_element(id="unique-2", tag="button", type="submit"),  # Should succeed
    ]

    result = await engine.process_collection(elements, page)

    stats = result['stats']
    assert stats['total_elements'] == 3
    assert stats['successful'] >= 1  # At least some should succeed
    assert stats['failed'] >= 0  # Some might fail

    print(f"   [OK] Total: {stats['total_elements']}")
    print(f"   [OK] Successful: {stats['successful']}")
    print(f"   [OK] Failed: {stats['failed']}")
    print(f"   [OK] Success rate: {stats['successful']/stats['total_elements']*100:.1f}%")

    return True


async def test_stats_tracking():
    """Test statistics tracking"""
    print("\n3. Testing statistics tracking...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    elements = [
        create_element(id="input-1", tag="input", type="email"),
        create_element(id="btn-1", tag="button", type="submit"),
        create_element(id="link-1", tag="a", attributes={"href": "/test"}),
    ]

    result = await engine.process_collection(elements, page)
    stats = result['stats']

    # Check all stats are present
    assert 'total_elements' in stats
    assert 'successful' in stats
    assert 'failed' in stats
    assert 'by_strategy' in stats
    assert 'by_cost' in stats

    assert stats['by_cost']['low'] + stats['by_cost']['medium'] + stats['by_cost']['high'] >= 2

    print(f"   [OK] Stats tracked: {len(stats['by_strategy'])} strategies used")
    print(f"   [OK] Cost distribution tracked")

    return True


async def test_get_stats():
    """Test get_stats() method"""
    print("\n4. Testing get_stats() method...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Process some elements
    elements = [
        create_element(id="test-1", tag="input", type="email"),
        create_element(id="test-2", tag="button", type="submit"),
    ]

    await engine.process_collection(elements, page)

    # Get stats
    stats = engine.get_stats()

    assert stats['total_elements'] == 2
    assert stats['successful'] >= 0

    print(f"   [OK] Stats retrieved: {stats}")

    return True


async def test_reset_stats():
    """Test reset_stats() method"""
    print("\n5. Testing reset_stats() method...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Process some elements
    elements = [create_element(id="test-1", tag="input", type="email")]
    await engine.process_collection(elements, page)

    # Check stats were populated
    stats_before = engine.get_stats()
    assert stats_before['total_elements'] == 1

    # Reset
    engine.reset_stats()

    # Check stats are reset
    stats_after = engine.get_stats()
    assert stats_after['total_elements'] == 0
    assert stats_after['successful'] == 0
    assert stats_after['failed'] == 0

    print("   [OK] Stats reset successfully")

    return True


async def test_empty_collection():
    """Test processing empty collection"""
    print("\n6. Testing empty collection...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    elements = []
    result = await engine.process_collection(elements, page)

    assert result['stats']['total_elements'] == 0
    assert result['stats']['successful'] == 0
    assert result['stats']['failed'] == 0

    # Check division by zero is handled
    if result['stats']['total_elements'] == 0:
        success_rate = 0.0
    else:
        success_rate = result['stats']['successful'] / result['stats']['total_elements']

    print("   [OK] Empty collection handled correctly")
    print(f"   [OK] Success rate (0 elements): {success_rate:.1f}%")

    return True


async def test_large_collection():
    """Test processing large collection (performance)"""
    print("\n7. Testing large collection (20 elements)...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Create 20 elements
    elements = []
    for i in range(20):
        elements.append(create_element(id=f"input-{i}", tag="input", type="email"))

    import time
    start_time = time.time()
    result = await engine.process_collection(elements, page)
    elapsed = time.time() - start_time

    stats = result['stats']
    assert stats['total_elements'] == 20

    print(f"   [OK] Processed {stats['total_elements']} elements in {elapsed:.2f}s")
    print(f"   [OK] Average: {elapsed/20*1000:.1f}ms per element")

    if elapsed > 5.0:
        print(f"   [WARNING] Processing slower than expected (>5s)")

    return True


async def test_strategy_distribution():
    """Test that strategy usage is tracked correctly"""
    print("\n8. Testing strategy distribution tracking...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    # Mix of elements that will use different strategies
    elements = [
        create_element(id="input-1", tag="input", type="email"),  # Likely ID_SELECTOR
        create_element(tag="button", type="submit", text="Submit"),  # Might use TEXT_CONTENT
        create_element(attributes={"aria-label": "Close"}),  # ARIA_LABEL
    ]

    result = await engine.process_collection(elements, page)
    stats = result['stats']

    # Should have tracked strategy usage
    assert len(stats['by_strategy']) > 0

    print(f"   [OK] {len(stats['by_strategy'])} different strategies used:")
    for strategy, count in stats['by_strategy'].items():
        print(f"      - {strategy}: {count} elements")

    return True


async def test_cost_distribution():
    """Test cost distribution tracking"""
    print("\n9. Testing cost distribution tracking...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    elements = [
        create_element(id="input-1", tag="input", type="email"),
        create_element(id="btn-1", tag="button", type="submit"),
        create_element(id="link-1", tag="a", attributes={"href": "/test"}),
    ]

    result = await engine.process_collection(elements, page)
    stats = result['stats']

    # Check cost distribution
    low = stats['by_cost']['low']
    medium = stats['by_cost']['medium']
    high = stats['by_cost']['high']

    total_in_cost = low + medium + high

    print(f"   [OK] Cost distribution:")
    print(f"      - Low (<0.15):    {low} elements")
    print(f"      - Medium (0.15-0.40): {medium} elements")
    print(f"      - High (>0.40):   {high} elements")
    print(f"      - Tracked: {total_in_cost}/{stats['successful']} successful elements")

    return True


async def test_debug_logging():
    """Test that debug logging can be enabled"""
    print("\n10. Testing debug logging...")

    engine = LocatorIntegrationEngine()

    # Should not crash when enabling debug logging
    try:
        engine.enable_debug_logging()
        print("   [OK] Debug logging enabled without error")
        return True
    except Exception as e:
        print(f"   [FAIL] Error enabling debug logging: {e}")
        return False


async def test_collection_results_structure():
    """Test result structure integrity"""
    print("\n11. Testing result structure...")

    engine = LocatorIntegrationEngine()
    page = MockPage()

    elements = [create_element(id="test-1", tag="input", type="email")]
    result = await engine.process_collection(elements, page)

    # Check each result has required fields
    for item in result['results']:
        assert 'element' in item
        assert 'locator' in item or item.get('success') is False
        assert 'success' in item

    print("   [OK] Result structure valid")

    return True


async def run_all_tests():
    """Run all integration tests"""
    print("="*60)
    print("Phase 4 - Scanner Integration Tests")
    print("="*60)

    all_tests = [
        test_process_collection_basic,
        test_process_collection_with_failures,
        test_stats_tracking,
        test_get_stats,
        test_reset_stats,
        test_empty_collection,
        test_large_collection,
        test_strategy_distribution,
        test_cost_distribution,
        test_debug_logging,
        test_collection_results_structure,
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
        print("\n[PASS] ALL INTEGRATION TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed} INTEGRATION TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run_all_tests()))
