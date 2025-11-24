"""
Tests for ContextV2 - Three-layer architecture
"""
import pytest
import time
from datetime import datetime
from selector_cli.core.element import Element
from selector_cli.core.context_v2 import ContextV2


class TestContextV2ThreeLayerModel:
    """Test the three-layer model (candidates, temp, workspace)"""

    def test_initial_state(self):
        """Test initial state of ContextV2"""
        ctx = ContextV2(enable_history_file=False)

        assert ctx.candidates == []
        assert ctx.temp == []
        assert ctx.workspace.is_empty()
        assert ctx.focus == 'candidates'
        assert ctx.candidates is not ctx._candidates  # Should return copy

    def test_candidates_setter(self):
        """Test setting candidates"""
        ctx = ContextV2(enable_history_file=False)
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
        ctx = ContextV2(enable_history_file=False)
        elements = [
            Element(index=2, uuid='c', tag='div'),
        ]

        ctx.temp = elements

        assert len(ctx.temp) == 1
        assert ctx.temp[0].tag == 'div'
        assert ctx._last_find_time is not None
        assert ctx.has_temp_results()

    def test_temp_expiration(self):
        """Test temp state expiration"""
        ctx = ContextV2(enable_history_file=False)
        ctx.TEMP_TTL = 1  # 1 second for testing

        # Set temp
        ctx.temp = [Element(index=0, uuid='a', tag='button')]
        assert len(ctx.temp) == 1
        assert ctx.has_temp_results()

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        assert len(ctx.temp) == 0
        assert not ctx.has_temp_results()

    def test_temp_clear(self):
        """Test clearing temp state"""
        ctx = ContextV2(enable_history_file=False)
        ctx.temp = [Element(index=0, uuid='a', tag='button')]

        assert len(ctx.temp) == 1
        assert ctx.focus == 'candidates'  # Initial focus

        # Change focus to temp
        ctx.focus = 'temp'
        assert ctx.focus == 'temp'

        # Clear temp
        ctx.clear_temp()

        assert len(ctx.temp) == 0
        assert ctx.focus == 'candidates'  # Focus reset
        assert ctx._last_find_time is None

    def test_workspace_operations(self):
        """Test workspace operations"""
        ctx = ContextV2(enable_history_file=False)
        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')

        # Add to workspace
        assert ctx.add_to_workspace(elem1) is True
        assert ctx.add_to_workspace(elem1) is False  # Duplicate
        assert ctx.add_to_workspace(elem2) is True

        assert len(ctx.workspace) == 2
        assert ctx.workspace.get(0) == elem1
        assert ctx.workspace.get(1) == elem2

        # Remove from workspace
        assert ctx.remove_from_workspace(elem1) is True
        assert ctx.remove_from_workspace(elem1) is False  # Not found
        assert len(ctx.workspace) == 1

        # Clear workspace
        ctx.clear_workspace()
        assert len(ctx.workspace) == 0

    def test_add_many_to_workspace(self):
        """Test adding multiple elements to workspace"""
        ctx = ContextV2(enable_history_file=False)
        elements = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
            Element(index=2, uuid='c', tag='div'),
        ]

        added = ctx.add_many_to_workspace(elements)

        assert added == 3
        assert len(ctx.workspace) == 3

        # Try adding again (should not duplicate)
        added = ctx.add_many_to_workspace(elements)
        assert added == 0
        assert len(ctx.workspace) == 3

    def test_element_by_index_from_layer(self):
        """Test getting element by index from different layers"""
        ctx = ContextV2(enable_history_file=False)

        # Setup layers
        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='div')

        ctx.candidates = [elem1, elem2]
        ctx.temp = [elem3]
        ctx.add_to_workspace(elem1)

        # Get from candidates
        assert ctx.get_element_by_index(0, 'candidates') == elem1
        assert ctx.get_element_by_index(1, 'candidates') == elem2
        assert ctx.get_element_by_index(2, 'candidates') is None

        # Get from temp
        assert ctx.get_element_by_index(2, 'temp') == elem3
        assert ctx.get_element_by_index(0, 'temp') is None

        # Get from workspace
        assert ctx.get_element_by_index(0, 'workspace') == elem1
        assert ctx.get_element_by_index(1, 'workspace') is None

    def test_elements_by_type_from_layer(self):
        """Test getting elements by type from different layers"""
        ctx = ContextV2(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='button')

        ctx.candidates = [elem1, elem2]
        ctx.add_to_workspace(elem3)

        # Get buttons from candidates
        buttons = ctx.get_elements_by_type('button', 'candidates')
        assert len(buttons) == 1
        assert buttons[0] == elem1

        # Get buttons from workspace
        buttons = ctx.get_elements_by_type('button', 'workspace')
        assert len(buttons) == 1
        assert buttons[0] == elem3

        # Get input from candidates
        inputs = ctx.get_elements_by_type('input', 'candidates')
        assert len(inputs) == 1
        assert inputs[0] == elem2

    def test_focus_management(self):
        """Test focus management"""
        ctx = ContextV2(enable_history_file=False)

        # Default focus
        assert ctx.focus == 'candidates'

        # Change focus
        ctx.focus = 'temp'
        assert ctx.focus == 'temp'

        ctx.focus = 'workspace'
        assert ctx.focus == 'workspace'

        # Invalid focus
        with pytest.raises(ValueError):
            ctx.focus = 'invalid'

    def test_get_focused_elements(self):
        """Test getting elements from focused layer"""
        ctx = ContextV2(enable_history_file=False)

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
        ctx.add_to_workspace(elem2)
        ctx.focus = 'workspace'
        focused = ctx.get_focused_elements()
        assert len(focused) == 1
        assert focused[0] == elem2

    def test_count_elements(self):
        """Test counting elements in different layers"""
        ctx = ContextV2(enable_history_file=False)

        ctx.candidates = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]
        ctx.temp = [Element(index=2, uuid='c', tag='div')]
        ctx.add_to_workspace(Element(index=3, uuid='d', tag='button'))

        assert ctx.count_elements('candidates') == 2
        assert ctx.count_elements('temp') == 1
        assert ctx.count_elements('workspace') == 1

    def test_is_empty(self):
        """Test checking if layers are empty"""
        ctx = ContextV2(enable_history_file=False)

        assert ctx.is_empty('candidates') is True
        assert ctx.is_empty('temp') is True
        assert ctx.is_empty('workspace') is True

        ctx.candidates = [Element(index=0, uuid='a', tag='button')]
        ctx.temp = [Element(index=1, uuid='b', tag='input')]
        ctx.add_to_workspace(Element(index=2, uuid='c', tag='div'))

        assert ctx.is_empty('candidates') is False
        assert ctx.is_empty('temp') is False
        assert ctx.is_empty('workspace') is False

    def test_has_temp_results(self):
        """Test checking if temp has valid results"""
        ctx = ContextV2(enable_history_file=False)
        ctx.TEMP_TTL = 2

        assert ctx.has_temp_results() is False

        ctx.temp = [Element(index=0, uuid='a', tag='button')]
        assert ctx.has_temp_results() is True

        time.sleep(2.5)
        assert ctx.has_temp_results() is False

    def test_get_state_summary(self):
        """Test debug state summary"""
        ctx = ContextV2(enable_history_file=False)

        # Empty state
        summary = ctx.get_state_summary()
        assert summary['candidates_count'] == 0
        assert summary['temp_count'] == 0
        assert summary['workspace_count'] == 0
        assert summary['focus'] == 'candidates'
        assert summary['temp_expired'] is True

        # Add elements
        ctx.candidates = [Element(index=0, uuid='a', tag='button')]
        ctx.temp = [Element(index=1, uuid='b', tag='input')]
        ctx.add_to_workspace(Element(index=2, uuid='c', tag='div'))
        ctx.focus = 'temp'

        summary = ctx.get_state_summary()
        assert summary['candidates_count'] == 1
        assert summary['temp_count'] == 1
        assert summary['workspace_count'] == 1
        assert summary['focus'] == 'temp'
        assert summary['temp_expired'] is False


class TestContextV2IntegrationWithV1:
    """Test that ContextV2 maintains compatibility with v1 concepts"""

    def test_history_management(self):
        """Test history management still works"""
        ctx = ContextV2(enable_history_file=False)

        ctx.add_to_history("scan")
        ctx.add_to_history("add button")
        ctx.add_to_history("list")

        assert len(ctx.history) == 3
        assert ctx.history[0] == "scan"
        assert ctx.get_last_command() == "list"
        assert ctx.get_history(2) == ["add button", "list"]

    def test_variable_management(self):
        """Test variable management still works"""
        ctx = ContextV2(enable_history_file=False)

        # Set variable
        assert ctx.set_variable("url", "https://example.com") is True
        assert ctx.get_variable("url") == "https://example.com"

        # Delete variable
        assert ctx.delete_variable("url") is True
        assert ctx.get_variable("url") is None
        assert ctx.delete_variable("nonexistent") is False

    def test_three_layers_independent(self):
        """Test that three layers maintain independent state"""
        ctx = ContextV2(enable_history_file=False)

        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='div')

        # Set different elements in each layer
        ctx.candidates = [elem1]
        ctx.temp = [elem2]
        ctx.add_to_workspace(elem3)

        # Check they're independent
        assert len(ctx.candidates) == 1
        assert len(ctx.temp) == 1
        assert len(ctx.workspace) == 1
        assert ctx.candidates[0] != ctx.temp[0]
        assert ctx.candidates[0] != ctx.workspace.get(2)
        assert ctx.temp[0] != ctx.workspace.get(2)

        # Modify temp (should not affect candidates)
        ctx.temp = [elem3]
        assert len(ctx.candidates) == 1
        assert ctx.candidates[0].tag == 'button'
        assert len(ctx.temp) == 1
        assert ctx.temp[0].tag == 'div'
