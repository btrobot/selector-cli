"""
Tests for Context - Three-layer architecture (v2 features)
"""
import pytest
import time
from datetime import datetime
from selector_cli.core.element import Element
from selector_cli.core.context import Context


class TestContextThreeLayerModel:
    """Test the three-layer model (candidates, temp, workspace)"""

    def test_initial_state(self):
        """Test initial state of Context with v2 features"""
        ctx = Context(enable_history_file=False)

        assert ctx.candidates == []
        assert ctx.temp == []
        assert ctx.workspace.is_empty()
        assert ctx.focus == 'candidates'
        # Check property returns copy, not direct reference
        assert ctx.candidates is not ctx._candidates

    def test_candidates_setter(self):
        """Test setting candidates"""
        ctx = Context(enable_history_file=False)
        elements = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]

        ctx.candidates = elements

        assert len(ctx.candidates) == 2
        assert ctx.candidates[0].tag == 'button'
        assert ctx.candidates[1].tag == 'input'
        assert ctx.last_scan_time is not None

    def test_temp_setter(self):
        """Test setting temp state"""
        ctx = Context(enable_history_file=False)
        elements = [
            Element(index=2, uuid='c', tag='div'),
        ]

        ctx.temp = elements

        assert len(ctx.temp) == 1
        assert ctx.temp[0].tag == 'div'

    def test_temp_copy_not_reference(self):
        """Test that temp property returns consistent reference"""
        ctx = Context(enable_history_file=False)
        ctx.temp = [Element(index=0, uuid='a', tag='button')]

        temp1 = ctx.temp
        temp2 = ctx.temp

        # Should be same list object (no copy needed without TTL)
        assert temp1 is temp2
        # But modifying temp still works
        assert len(temp1) == 1
        assert temp1[0].tag == 'button'

    def test_focus_management(self):
        """Test focus management"""
        ctx = Context(enable_history_file=False)

        # Default focus
        assert ctx.focus == 'candidates'

        # Change focus
        ctx.focus = 'temp'
        assert ctx.focus == 'temp'

        ctx.focus = 'workspace'
        assert ctx.focus == 'workspace'

        # Change back
        ctx.focus = 'candidates'
        assert ctx.focus == 'candidates'

    def test_get_focused_elements(self):
        """Test getting elements from focused layer"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # Setup candidates
        ctx.candidates = [elem1, elem2]
        ctx.focus = 'candidates'
        assert ctx.get_focused_elements() == [elem1, elem2]

        # Setup temp
        ctx.temp = [elem1]
        ctx.focus = 'temp'
        assert ctx.get_focused_elements() == [elem1]

        # Setup workspace
        ctx.workspace.add(elem2)
        ctx.focus = 'workspace'
        focused = ctx.get_focused_elements()
        assert len(focused) == 1
        assert focused[0] == elem2

    def test_three_layers_independent(self):
        """Test that three layers maintain independent state"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='div')

        # Set different elements in each layer
        ctx.candidates = [elem1]
        ctx.temp = [elem2]
        ctx.workspace.add(elem3)

        # Check they're independent
        assert len(ctx.candidates) == 1
        assert len(ctx.temp) == 1
        assert len(ctx.workspace.elements) == 1

        # Check they're different elements
        assert ctx.candidates[0].uuid == 'a'
        assert ctx.temp[0].uuid == 'b'
        assert list(ctx.workspace.elements)[0].uuid == 'c'

        # Modify temp (should not affect candidates)
        ctx.temp = [elem3]
        assert len(ctx.candidates) == 1
        assert ctx.candidates[0].tag == 'button'
        assert len(ctx.temp) == 1
        assert ctx.temp[0].tag == 'div'


class TestContextV1BackwardCompatibility:
    """Test that Context maintains compatibility with v1 concepts"""

    def test_history_management(self):
        """Test history management still works"""
        ctx = Context(enable_history_file=False)

        ctx.add_to_history("scan")
        ctx.add_to_history("add button")
        ctx.add_to_history("list")

        assert len(ctx.history) == 3
        assert ctx.history[0] == "scan"
        assert ctx.get_last_command() == "list"
        assert ctx.get_history(2) == ["add button", "list"]

    def test_variable_management(self):
        """Test variable management still works"""
        ctx = Context(enable_history_file=False)

        # Set variable
        assert ctx.set_variable("url", "https://example.com") is True
        assert ctx.get_variable("url") == "https://example.com"

        # Delete variable
        assert ctx.delete_variable("url") is True
        assert ctx.get_variable("url") is None
        assert ctx.delete_variable("nonexistent") is False

    def test_all_elements_backward_compatible(self):
        """Test that all_elements property works for v1 compatibility"""
        ctx = Context(enable_history_file=False)

        # In v1, all_elements was the main storage
        # In v2, it maps to candidates
        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # Setting all_elements (v1 style) should set candidates
        ctx.all_elements = [elem1, elem2]

        # Should be accessible via both all_elements and candidates
        assert len(ctx.all_elements) == 2
        assert len(ctx.candidates) == 2
        assert ctx.all_elements[0].tag == 'button'
        assert ctx.candidates[0].tag == 'button'

        # They should point to the same underlying data
        # (but note that the property returns a copy, so we test that)
        assert ctx.all_elements is not ctx.all_elements  # Different copies

    def test_collection_backward_compatible(self):
        """Test that collection (workspace) works for v1 compatibility"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')

        # In v1, collection was the user collection
        # In v2, it's the same, but also accessible as workspace
        ctx.collection.add(elem1)

        # Should be accessible via both collection and workspace
        assert len(ctx.collection.elements) == 1
        assert len(ctx.workspace.elements) == 1
        assert list(ctx.collection.elements)[0] == elem1
        assert list(ctx.workspace.elements)[0] == elem1

    def test_update_elements_backward_compatible(self):
        """Test that update_elements works for v1 compatibility"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # update_elements is v1 method
        ctx.update_elements([elem1, elem2])

        # Should update candidates
        assert len(ctx.candidates) == 2
        assert ctx.last_scan_time is not None

    def test_get_element_by_index_backward_compatible(self):
        """Test that get_element_by_index works from candidates"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        ctx.candidates = [elem1, elem2]

        assert ctx.get_element_by_index(0) == elem1
        assert ctx.get_element_by_index(1) == elem2
        assert ctx.get_element_by_index(999) is None

    def test_get_elements_by_type_backward_compatible(self):
        """Test that get_elements_by_type works from candidates"""
        ctx = Context(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='button')

        ctx.candidates = [elem1, elem2, elem3]

        buttons = ctx.get_elements_by_type('button')
        assert len(buttons) == 2
        assert buttons[0].tag == 'button'
        assert buttons[1].tag == 'button'

        inputs = ctx.get_elements_by_type('input')
        assert len(inputs) == 1
        assert inputs[0].tag == 'input'


