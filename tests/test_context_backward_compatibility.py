"""
Backward compatibility test for Context - ensures v1 API still works after v2 enhancements
"""
import pytest
from selector_cli.core.context import Context
from selector_cli.core.element import Element


class TestContextBackwardCompatibility:
    """Test that v1 API still works after v2 enhancements"""

    def test_v1_all_elements_still_works(self):
        """Test that all_elements (v1) can be set and accessed"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # v1 style: set all_elements
        ctx.all_elements = [elem1, elem2]

        # Should be accessible
        assert len(ctx.all_elements) == 2
        assert ctx.all_elements[0].tag == 'button'
        assert ctx.all_elements[1].tag == 'input'

        # And maps to candidates
        assert len(ctx.candidates) == 2

    def test_v1_collection_still_works(self):
        """Test that collection (v1) can be used"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')

        # v1 style: use collection
        ctx.collection.add(elem1)

        # Should be accessible
        assert len(ctx.collection.elements) == 1

        # And maps to workspace
        assert len(ctx.workspace.elements) == 1

    def test_v1_update_elements_still_works(self):
        """Test that update_elements method still works"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # v1 style: update_elements
        ctx.update_elements([elem1, elem2])

        # Should update candidates
        assert len(ctx.candidates) == 2
        assert ctx.last_scan_time is not None

    def test_v1_get_element_by_index_still_works(self):
        """Test that get_element_by_index method still works"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')

        ctx.candidates = [elem1]

        # v1 style: get element by index
        result = ctx.get_element_by_index(0)
        assert result == elem1

        # Non-existent index
        result = ctx.get_element_by_index(999)
        assert result is None

    def test_v1_get_elements_by_type_still_works(self):
        """Test that get_elements_by_type method still works"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        ctx.candidates = [elem1, elem2]

        # v1 style: get elements by type
        buttons = ctx.get_elements_by_type('button')
        assert len(buttons) == 1
        assert buttons[0].tag == 'button'

        inputs = ctx.get_elements_by_type('input')
        assert len(inputs) == 1
        assert inputs[0].tag == 'input'

    def test_v1_history_management_still_works(self):
        """Test that history management still works"""
        ctx = Context(enable_history_file=False)

        # v1 style: add to history
        ctx.add_to_history("scan button")
        ctx.add_to_history("add button")

        assert len(ctx.history) == 2
        assert ctx.history[0] == "scan button"
        assert ctx.get_last_command() == "add button"

    def test_v1_variable_management_still_works(self):
        """Test that variable management still works"""
        ctx = Context(enable_history_file=False)

        # v1 style: set variable
        assert ctx.set_variable("url", "https://example.com") is True
        assert ctx.get_variable("url") == "https://example.com"

        # Delete variable
        assert ctx.delete_variable("url") is True
        assert ctx.get_variable("url") is None

    def test_v1_v2_api_can_be_used_together(self):
        """Test that v1 and v2 APIs can be mixed"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # Use v1 API (all_elements)
        ctx.all_elements = [elem1, elem2]

        # Use v2 API (temp)
        elem3 = Element(index=2, uuid='c', tag='div')
        ctx.temp = [elem3]

        # Both should work
        assert len(ctx.all_elements) == 2
        assert len(ctx.candidates) == 2
        assert len(ctx.temp) == 1

        # Use v1 API (collection)
        ctx.collection.add(elem1)

        # Use v2 API (workspace)
        assert len(ctx.workspace.elements) == 1
        assert len(ctx.collection.elements) == 1

    def test_v1_api_does_not_break_v2_behavior(self):
        """Test that using v1 API doesn't break v2 behavior"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')

        # Use v1 API
        ctx.all_elements = [elem1]

        # v2 behavior should still work
        assert ctx.candidates[0] == elem1
        assert ctx.has_temp_results() is False  # Temp is empty

        # v2 TTL should work
        ctx.temp = [elem1]
        assert ctx.has_temp_results() is True
