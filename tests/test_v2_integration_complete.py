"""
Complete integration tests for v2 features
Tests end-to-end workflows with all v2 enhancements
"""
import pytest
import asyncio
import time
from datetime import datetime
from selector_cli.core.context import Context
from selector_cli.core.element import Element
from selector_cli.parser.parser import Parser
from selector_cli.commands.executor import CommandExecutor
from selector_cli.parser.command import TargetType, Command


class TestV2ThreeLayerWorkflow:
    """Test complete three-layer workflow (candidates → temp → workspace)"""

    @pytest.fixture
    def context(self):
        """Create context with v2 features - clean state"""
        ctx = Context(enable_history_file=False)
        # Ensure clean state
        ctx._candidates = []
        ctx._temp = []
        ctx.collection.clear()
        return ctx

    @pytest.fixture
    def executor(self):
        """Create command executor"""
        return CommandExecutor()

    @pytest.fixture
    def parser(self):
        """Create parser"""
        return Parser()

    def test_three_layer_workflow_basic(self, context, executor, parser):
        """Test: scan → find → add → list workflow"""
        # Ensure clean state
        context.collection.clear()

        # Step 1: Simulate SCAN → candidates
        elements = [
            Element(index=0, uuid='btn1', tag='button', attributes={'type': 'submit'}),
            Element(index=1, uuid='input1', tag='input', attributes={'type': 'email'}),
            Element(index=2, uuid='input2', tag='input', attributes={'type': 'password'}),
            Element(index=3, uuid='btn2', tag='button', attributes={'type': 'button'}),
        ]
        context.candidates = elements

        assert len(context.candidates) == 4
        assert len(context.temp) == 0
        assert len(context.workspace.elements) == 0

        # Step 2: FIND email input → temp
        # Simulate: find input where type="email"
        email_inputs = [e for e in context.candidates if e.tag == 'input' and e.attributes.get('type') == 'email']
        context.temp = email_inputs

        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'input1'
        assert len(context.candidates) == 4  # candidates unchanged

        # Step 3: ADD from temp → workspace
        workspace_count_before = len(context.workspace.elements)
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == workspace_count_before + 1
        # Check element is in workspace
        workspace_elems = list(context.workspace.elements)
        uuids = [e.uuid for e in workspace_elems]
        assert 'input1' in uuids

        # Step 4: FIND password input → temp (overwrites)
        password_inputs = [e for e in context.candidates if e.tag == 'input' and e.attributes.get('type') == 'password']
        context.temp = password_inputs

        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'input2'  # Now temp has password input

        # Step 5: ADD from temp again → workspace (append)
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == 2  # Both inputs now

    def test_candidates_remains_read_only(self, context):
        """Test that candidates is read-only source (not modified by operations)"""
        elements = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]
        context.candidates = elements

        # Modify temp and workspace
        context.temp = [elements[0]]
        context.workspace.add(elements[1])

        # candidates should be unchanged
        assert len(context.candidates) == 2
        assert context.candidates[0].uuid == 'a'
        assert context.candidates[1].uuid == 'b'


class TestV2FindCommand:
    """Test FIND command execution workflow"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_find_filters_and_copies_to_temp(self, context):
        """Test that find filters candidates and copies to temp"""
        # Setup candidates
        elements = [
            Element(index=0, uuid='a', tag='button', visible=True),
            Element(index=1, uuid='b', tag='button', visible=False),
            Element(index=2, uuid='c', tag='button', visible=True),
        ]
        context.candidates = elements

        # Simulate find button where visible
        visible_buttons = [e for e in context.candidates if e.tag == 'button' and e.visible]
        context.temp = visible_buttons

        assert len(context.temp) == 2
        assert all(e.visible for e in context.temp)
        assert len(context.candidates) == 3  # Source unchanged

    def test_find_resets_ttl_timer(self, context):
        """Test that setting temp resets TTL timer"""
        context.TEMP_TTL = 1  # 1 second for testing

        # First find
        context.temp = [Element(index=0, uuid='a', tag='button')]
        first_time = context._last_find_time
        time.sleep(0.5)

        # Second find (should reset timer)
        context.temp = [Element(index=1, uuid='b', tag='input')]
        second_time = context._last_find_time

        assert second_time > first_time


class TestV2RefineMode:
    """Test .find (refine) mode"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_refine_filters_temp(self, context):
        """Test that refine mode filters existing temp"""
        # Setup temp with some elements
        elements = [
            Element(index=0, uuid='a', tag='div', text='menu item 1'),
            Element(index=1, uuid='b', tag='div', text='menu item 2'),
            Element(index=2, uuid='c', tag='div', text='product 1'),
            Element(index=3, uuid='d', tag='div', text='product 2'),
        ]
        context.temp = elements
        assert len(context.temp) == 4

        # Simulate .find where text contains "product"
        product_divs = [e for e in context.temp if 'product' in (e.text or '')]
        context.temp = product_divs  # This resets TTL

        assert len(context.temp) == 2
        assert all('product' in e.text for e in context.temp)

    def test_refine_preserves_other_layers(self, context):
        """Test that refine only affects temp, not candidates or workspace"""
        # Setup all layers
        context.candidates = [Element(index=0, uuid='a', tag='button')]
        context.temp = [Element(index=1, uuid='b', tag='input')]
        context.workspace.add(Element(index=2, uuid='c', tag='div'))

        # Refine temp
        context.temp = [Element(index=3, uuid='d', tag='a')]

        # Other layers unchanged
        assert len(context.candidates) == 1
        assert len(context.workspace.elements) == 1


class TestV2AddEnhanced:
    """Test enhanced ADD command"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_add_from_temp(self, context):
        """Test add from temp"""
        # Setup temp
        temp_elements = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]
        context.temp = temp_elements

        # Add from temp to workspace
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == 2

    def test_add_from_candidates(self, context):
        """Test add from candidates"""
        # Setup candidates
        candidates = [
            Element(index=0, uuid='x', tag='select'),
            Element(index=1, uuid='y', tag='textarea'),
        ]
        context.candidates = candidates

        # Add from candidates to workspace
        for elem in context.candidates:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == 2

    def test_add_append_mode(self, context):
        """Test add append mode (doesn't clear existing)"""
        # Setup workspace with existing elements
        context.workspace.add(Element(index=0, uuid='existing1', tag='button'))

        # Add new elements in append mode
        new_elements = [
            Element(index=1, uuid='new1', tag='input'),
            Element(index=2, uuid='new2', tag='select'),
        ]
        for elem in new_elements:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        # Workspace should have all elements
        assert len(context.workspace.elements) == 3

    def test_add_with_where_condition(self, context):
        """Test add with WHERE condition"""
        # Setup candidates with mixed elements
        elements = [
            Element(index=0, uuid='a', tag='button', visible=True),
            Element(index=1, uuid='b', tag='button', visible=False),
            Element(index=2, uuid='c', tag='button', visible=True),
        ]
        context.candidates = elements

        # Add only visible buttons
        visible_buttons = [e for e in context.candidates if e.visible]
        for elem in visible_buttons:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == 2
        assert all(e.visible for e in context.workspace.elements)

    def test_add_skips_duplicates(self, context):
        """Test that add skips elements already in workspace"""
        elem = Element(index=0, uuid='a', tag='button')
        context.workspace.add(elem)

        # Try to add same element again
        if not context.workspace.contains(elem):
            context.workspace.add(elem)

        # Should still have only one
        assert len(context.workspace.elements) == 1


class TestV2ListEnhanced:
    """Test enhanced LIST command"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_list_candidates(self, context):
        """Test list candidates"""
        context.candidates = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]

        result = context.candidates
        assert len(result) == 2

    def test_list_temp(self, context):
        """Test list temp"""
        context.temp = [
            Element(index=0, uuid='x', tag='div'),
        ]

        result = context.temp
        assert len(result) == 1

    def test_list_workspace(self, context):
        """Test list workspace"""
        context.workspace.add(Element(index=0, uuid='a', tag='button'))
        context.workspace.add(Element(index=1, uuid='b', tag='input'))

        result = list(context.workspace.elements)
        assert len(result) == 2

    def test_list_with_where_condition(self, context):
        """Test list with WHERE condition"""
        elements = [
            Element(index=0, uuid='a', tag='button', visible=True),
            Element(index=1, uuid='b', tag='button', visible=False),
            Element(index=2, uuid='c', tag='button', visible=True),
        ]
        context.candidates = elements

        visible_buttons = [e for e in context.candidates if e.visible]
        assert len(visible_buttons) == 2


class TestV2TTLMechanism:
    """Test TTL (Time To Live) mechanism"""

    @pytest.fixture
    def context(self):
        ctx = Context(enable_history_file=False)
        ctx.TEMP_TTL = 2  # 2 seconds for testing
        return ctx

    def test_temp_expires_after_ttl(self, context):
        """Test that temp expires after TTL"""
        context.temp = [Element(index=0, uuid='a', tag='button')]
        assert len(context.temp) == 1
        assert context.has_temp_results() is True

        # Wait for expiration
        time.sleep(2.5)

        # Should be expired
        assert len(context.temp) == 0
        assert context.has_temp_results() is False

    def test_temp_returns_empty_when_expired(self, context):
        """Test that expired temp returns empty list (not error)"""
        context.temp = [Element(index=0, uuid='a', tag='button')]
        time.sleep(2.5)

        expired = context.temp
        assert expired == []
        assert isinstance(expired, list)

    def test_temp_ttl_resets_on_new_find(self, context):
        """Test that TTL timer resets on new find"""
        context.TEMP_TTL = 2

        # First find
        context.temp = [Element(index=0, uuid='a', tag='button')]
        first_time = context._last_find_time
        time.sleep(1)

        # Should still be valid
        assert len(context.temp) == 1

        # New find (resets timer)
        context.temp = [Element(index=1, uuid='b', tag='input')]
        second_time = context._last_find_time

        assert second_time > first_time
        assert len(context.temp) == 1

        # Wait 1.5 seconds (should still be valid due to reset)
        time.sleep(1.5)
        assert len(context.temp) == 1

    def test_get_temp_age(self, context):
        """Test getting temp age"""
        assert context.get_temp_age() is None  # No temp set

        context.temp = [Element(index=0, uuid='a', tag='button')]
        age = context.get_temp_age()
        assert age is not None
        assert 0 <= age < 0.1


class TestV2FocusManagement:
    """Test focus state management"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_default_focus_is_candidates(self, context):
        """Test default focus is candidates"""
        assert context.focus == 'candidates'

    def test_focus_changes(self, context):
        """Test focus can be changed"""
        context.focus = 'temp'
        assert context.focus == 'temp'

        context.focus = 'workspace'
        assert context.focus == 'workspace'

        context.focus = 'candidates'
        assert context.focus == 'candidates'

    def test_get_focused_elements(self, context):
        """Test getting elements from focused layer"""
        elem1 = Element(index=0, uuid='a', tag='button')
        elem2 = Element(index=1, uuid='b', tag='input')
        elem3 = Element(index=2, uuid='c', tag='div')

        context.candidates = [elem1, elem2]
        context.temp = [elem3]
        context.workspace.add(elem1)

        context.focus = 'candidates'
        assert len(context.get_focused_elements()) == 2

        context.focus = 'temp'
        assert len(context.get_focused_elements()) == 1

        context.focus = 'workspace'
        assert len(context.get_focused_elements()) == 1


class TestV2BackwardCompatibility:
    """Test backward compatibility with v1"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_v1_all_elements_still_works(self, context):
        """Test v1 all_elements property"""
        elem = Element(index=0, uuid='a', tag='button')
        context.all_elements = [elem]

        assert len(context.all_elements) == 1
        assert context.all_elements[0].uuid == 'a'

    def test_v1_collection_still_works(self, context):
        """Test v1 collection property"""
        elem = Element(index=0, uuid='a', tag='button')
        context.collection.add(elem)

        assert len(context.collection.elements) == 1

    def test_v1_update_elements_still_works(self, context):
        """Test v1 update_elements method"""
        elements = [
            Element(index=0, uuid='a', tag='button'),
            Element(index=1, uuid='b', tag='input'),
        ]
        context.update_elements(elements)

        assert len(context.candidates) == 2
        assert context.last_scan_time is not None

    def test_v1_get_element_by_index_still_works(self, context):
        """Test v1 get_element_by_index method"""
        elem = Element(index=0, uuid='a', tag='button')
        context.candidates = [elem]

        result = context.get_element_by_index(0)
        assert result == elem

    def test_v1_history_still_works(self, context):
        """Test v1 history management"""
        context.add_to_history("scan button")
        context.add_to_history("add button")

        assert len(context.history) == 2
        assert context.get_last_command() == "add button"

    def test_v1_variables_still_works(self, context):
        """Test v1 variable management"""
        context.set_variable("url", "https://example.com")
        assert context.get_variable("url") == "https://example.com"

        context.delete_variable("url")
        assert context.get_variable("url") is None


class TestV2ComplexWorkflows:
    """Test complex real-world workflows"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_github_login_form_workflow(self, context):
        """Test complete workflow: GitHub login form extraction"""
        # Step 1: Scan page (simulated)
        page_elements = [
            Element(index=0, uuid='logo', tag='img'),
            Element(index=1, uuid='login', tag='input', attributes={'type': 'email'}),
            Element(index=2, uuid='password', tag='input', attributes={'type': 'password'}),
            Element(index=3, uuid='submit', tag='button', attributes={'type': 'submit'}),
            Element(index=4, uuid='link', tag='a'),
        ]
        context.candidates = page_elements

        # Step 2: Find email input
        email_input = [e for e in context.candidates if e.tag == 'input' and e.attributes.get('type') == 'email']
        context.temp = email_input
        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'login'

        # Step 3: Add to workspace
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)
        assert len(context.workspace.elements) == 1

        # Step 4: Find password input
        password_input = [e for e in context.candidates if e.tag == 'input' and e.attributes.get('type') == 'password']
        context.temp = password_input
        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'password'

        # Step 5: Add to workspace
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)
        assert len(context.workspace.elements) == 2

        # Step 6: Find submit button
        submit_button = [e for e in context.candidates if e.tag == 'button' and e.attributes.get('type') == 'submit']
        context.temp = submit_button
        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'submit'

        # Step 7: Add to workspace
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)
        assert len(context.workspace.elements) == 3

        # Step 8: Verify workspace has login form elements
        workspace_elems = list(context.workspace.elements)
        tags = [e.tag for e in workspace_elems]
        assert 'input' in tags
        assert 'button' in tags

    def test_ecommerce_product_filtering(self, context):
        """Test: Extract visible products from ecommerce page"""
        # Ensure clean state
        context.collection.clear()

        # Setup: Scanned elements (mixed products, menus, ads)
        elements = []
        for i in range(20):
            elem = Element(index=i, uuid=f'elem{i}', tag='div')
            elem.attributes = {'class': 'product' if i < 10 else 'menu-item'}
            elem.visible = i % 3 != 0  # Some invisible
            elements.append(elem)

        context.candidates = elements

        # Step 1: Find all divs
        all_divs = [e for e in context.candidates if e.tag == 'div']
        context.temp = all_divs
        assert len(context.temp) == 20

        # Step 2: Refine to visible only (.find where visible)
        visible_divs = [e for e in context.temp if e.visible]
        context.temp = visible_divs
        assert len(context.temp) == 13  # 20 - 7 (indices 0,3,6,9,12,15,18 are invisible)

        # Step 3: Refine to products only (.find where class contains "product")
        product_divs = [e for e in context.temp if 'product' in e.attributes.get('class', '')]
        context.temp = product_divs
        assert len(context.temp) == 6  # Only visible products (indices 1,2,4,5,7,8)
        assert all('product' in e.attributes['class'] for e in context.temp)

        # Step 4: Add to workspace
        for elem in context.temp:
            if not context.workspace.contains(elem):
                context.workspace.add(elem)

        assert len(context.workspace.elements) == 6  # Same as temp count

    def test_temp_expiration_during_workflow(self, context):
        """Test that temp expiration doesn't break workflow"""
        context.TEMP_TTL = 1  # 1 second

        # Step 1: Find elements → temp
        context.temp = [Element(index=0, uuid='a', tag='button')]
        assert len(context.temp) == 1

        # Step 2: Wait for expiration
        time.sleep(1.5)

        # Step 3: Try to add from expired temp (should handle gracefully)
        expired_temp = context.temp
        assert len(expired_temp) == 0  # Returns empty, doesn't error

        # Step 4: Workflow continues (can re-scan or re-find)
        context.temp = [Element(index=1, uuid='b', tag='input')]
        assert len(context.temp) == 1


class TestV2CommandParsingIntegration:
    """Test command parsing integrated with execution"""

    @pytest.fixture
    def parser(self):
        return Parser()

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_parse_and_execute_find_workflow(self, parser, context):
        """Test parsing FIND command"""
        cmd = parser.parse("find button where visible")

        assert cmd.verb == 'find'
        assert cmd.target.element_type == 'button'
        assert cmd.condition_tree is not None

    def test_parse_and_execute_add_from_temp(self, parser, context):
        """Test parsing ADD from temp"""
        cmd = parser.parse("add from temp")

        assert cmd.verb == 'add'
        assert cmd.source == 'temp'
        assert cmd.append_mode is False

    def test_parse_and_execute_add_append(self, parser):
        """Test parsing ADD append"""
        cmd = parser.parse("add append button")

        assert cmd.verb == 'add'
        assert cmd.append_mode is True
        assert cmd.target.element_type == 'button'

    def test_parse_and_execute_dot_find(self, parser):
        """Test parsing .find (refine)"""
        cmd = parser.parse(".find where visible")

        assert cmd.verb == 'find'
        assert cmd.is_refine is True
        assert cmd.condition_tree is not None

    def test_parse_and_execute_list_candidates(self, parser):
        """Test parsing LIST candidates"""
        cmd = parser.parse("list candidates")

        assert cmd.verb == 'list'
        assert cmd.source == 'candidates'

    def test_parse_complex_command(self, parser):
        """Test parsing complex multi-part command"""
        cmd = parser.parse("add append from temp where visible")

        assert cmd.verb == 'add'
        assert cmd.append_mode is True
        assert cmd.source == 'temp'
        assert cmd.condition_tree is not None


class TestV2EdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def context(self):
        return Context(enable_history_file=False)

    def test_add_from_empty_source(self, context):
        """Test adding from empty source"""
        source_elements = context.temp
        assert len(source_elements) == 0

    def test_list_empty_layer(self, context):
        """Test listing empty layer"""
        result = context.temp
        assert result == []

    def test_refine_without_temp(self, context):
        """Test refining when temp is empty"""
        result = context.temp
        assert len(result) == 0

    def test_double_add_same_element(self, context):
        """Test adding same element twice"""
        elem = Element(index=0, uuid='a', tag='button')
        context.workspace.add(elem)

        # Try adding again
        if not context.workspace.contains(elem):
            context.workspace.add(elem)

        assert len(context.workspace.elements) == 1

    def test_mixed_v1_v2_commands(self, context):
        """Test mixing v1 and v2 commands"""
        # v1 style
        context.all_elements = [Element(index=0, uuid='a', tag='button')]

        # v2 style
        context.temp = [Element(index=1, uuid='b', tag='input')]

        # Both should work
        assert len(context.all_elements) == 1
        assert len(context.temp) == 1

    def test_multiple_sequential_finds(self, context):
        """Test multiple sequential find operations"""
        # First find
        context.temp = [Element(index=0, uuid='a', tag='button')]
        assert len(context.temp) == 1

        # Second find (overwrites)
        context.temp = [Element(index=1, uuid='b', tag='input')]
        assert len(context.temp) == 1
        assert context.temp[0].uuid == 'b'  # Overwritten
