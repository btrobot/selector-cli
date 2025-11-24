"""
Tests for Parser v2 features - FIND command, enhanced ADD/LIST
"""
import pytest
from selector_cli.parser.parser import Parser
from selector_cli.parser.command import (
    TargetType, Operator, ConditionType, LogicOp
)


class TestParserFindCommand:
    """Test FIND command parsing"""

    def test_parse_find_basic(self):
        """Test basic FIND command"""
        parser = Parser()
        cmd = parser.parse("find button")

        assert cmd.verb == 'find'
        assert cmd.target is not None
        assert cmd.target.type == TargetType.ELEMENT_TYPE
        assert cmd.target.element_type == 'button'
        assert cmd.condition_tree is None
        assert cmd.is_refine is False

    def test_parse_find_with_where(self):
        """Test FIND with WHERE clause"""
        parser = Parser()
        cmd = parser.parse('find input where type="email"')

        assert cmd.verb == 'find'
        assert cmd.target.element_type == 'input'
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.type == ConditionType.SIMPLE

    def test_parse_find_multiple_types(self):
        """Test FIND with multiple element types (comma-separated)"""
        parser = Parser()
        cmd = parser.parse("find button,input")

        assert cmd.verb == 'find'
        assert cmd.target is not None
        # For now, we parse the first type
        assert cmd.target.element_type in ['button', 'input']

    def test_parse_dot_find_refine(self):
        """Test .find (refine mode)"""
        parser = Parser()
        cmd = parser.parse(".find where visible")

        assert cmd.verb == 'find'
        assert cmd.is_refine is True
        assert cmd.target is None  # Refine mode doesn't need target
        assert cmd.condition_tree is not None

    def test_parse_dot_find_without_where(self):
        """Test .find without WHERE clause"""
        parser = Parser()
        cmd = parser.parse(".find")

        assert cmd.verb == 'find'
        assert cmd.is_refine is True
        assert cmd.condition_tree is None

    def test_parse_find_with_complex_condition(self):
        """Test FIND with complex WHERE clause"""
        parser = Parser()
        cmd = parser.parse('find button where visible and text contains "Submit"')

        assert cmd.verb == 'find'
        assert cmd.target.element_type == 'button'
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.type == ConditionType.COMPOUND


class TestParserAddEnhanced:
    """Test enhanced ADD command with v2 features"""

    def test_parse_add_from_temp(self):
        """Test ADD from temp"""
        parser = Parser()
        cmd = parser.parse("add from temp")

        assert cmd.verb == 'add'
        assert cmd.source == 'temp'
        assert cmd.append_mode is False
        assert cmd.target is None

    def test_parse_add_from_candidates(self):
        """Test ADD from candidates"""
        parser = Parser()
        cmd = parser.parse("add from candidates")

        assert cmd.verb == 'add'
        assert cmd.source == 'candidates'

    def test_parse_add_from_workspace(self):
        """Test ADD from workspace"""
        parser = Parser()
        cmd = parser.parse("add from workspace")

        assert cmd.verb == 'add'
        assert cmd.source == 'workspace'

    def test_parse_add_append(self):
        """Test ADD append mode"""
        parser = Parser()
        cmd = parser.parse("add append button")

        assert cmd.verb == 'add'
        assert cmd.append_mode is True
        assert cmd.target.element_type == 'button'

    def test_parse_add_from_temp_with_where(self):
        """Test ADD from temp with WHERE clause"""
        parser = Parser()
        cmd = parser.parse("add from temp where visible")

        assert cmd.verb == 'add'
        assert cmd.source == 'temp'
        assert cmd.condition_tree is not None

    def test_parse_add_append_from_candidates(self):
        """Test ADD append from candidates"""
        parser = Parser()
        cmd = parser.parse("add append from candidates where visible")

        assert cmd.verb == 'add'
        assert cmd.append_mode is True
        assert cmd.source == 'candidates'
        assert cmd.condition_tree is not None

    def test_parse_add_v1_backward_compatible(self):
        """Test ADD v1 syntax still works"""
        parser = Parser()
        cmd = parser.parse("add button")

        assert cmd.verb == 'add'
        assert cmd.source is None
        assert cmd.append_mode is False
        assert cmd.target.element_type == 'button'


class TestParserListEnhanced:
    """Test enhanced LIST command with v2 features"""

    def test_parse_list_candidates(self):
        """Test LIST candidates"""
        parser = Parser()
        cmd = parser.parse("list candidates")

        assert cmd.verb == 'list'
        assert cmd.source == 'candidates'

    def test_parse_list_temp(self):
        """Test LIST temp"""
        parser = Parser()
        cmd = parser.parse("list temp")

        assert cmd.verb == 'list'
        assert cmd.source == 'temp'

    def test_parse_list_workspace(self):
        """Test LIST workspace"""
        parser = Parser()
        cmd = parser.parse("list workspace")

        assert cmd.verb == 'list'
        assert cmd.source == 'workspace'

    def test_parse_list_v1_backward_compatible(self):
        """Test LIST v1 syntax still works"""
        parser = Parser()

        # Plain list
        cmd = parser.parse("list")
        assert cmd.verb == 'list'
        assert cmd.source is None  # Will default to workspace in executor

        # List with target
        cmd = parser.parse("list button")
        assert cmd.verb == 'list'
        assert cmd.target.element_type == 'button'

    def test_parse_list_with_where(self):
        """Test LIST with WHERE clause"""
        parser = Parser()
        cmd = parser.parse("list temp where visible")

        assert cmd.verb == 'list'
        assert cmd.source == 'temp'
        assert cmd.condition_tree is not None


class TestParserV2CommandFields:
    """Test that v2 Command fields are properly set"""

    def test_command_v2_fields_defaults(self):
        """Test that v2 fields have proper defaults"""
        from selector_cli.parser.command import Command

        cmd = Command(verb='test', raw='test')

        # Should have v2 fields with None/False defaults
        assert cmd.source is None
        assert cmd.append_mode is False
        assert cmd.is_refine is False

    def test_parse_find_sets_is_refine_false(self):
        """Test that regular find sets is_refine=False"""
        parser = Parser()
        cmd = parser.parse("find button")

        assert cmd.is_refine is False
        assert cmd.verb == 'find'

    def test_parse_dot_find_sets_is_refine_true(self):
        """Test that .find sets is_refine=True"""
        parser = Parser()
        cmd = parser.parse(".find where visible")

        assert cmd.is_refine is True
        assert cmd.verb == 'find'

    def test_parse_add_from_temp_sets_source(self):
        """Test that add from temp sets source field"""
        parser = Parser()
        cmd = parser.parse("add from temp")

        assert cmd.source == 'temp'
        assert cmd.append_mode is False

    def test_parse_add_append_sets_append_mode(self):
        """Test that add append sets append_mode field"""
        parser = Parser()
        cmd = parser.parse("add append button")

        assert cmd.append_mode is True
        assert cmd.source is None
        assert cmd.target is not None

    def test_parse_multiple_v2_fields(self):
        """Test that multiple v2 fields can be set together"""
        parser = Parser()
        cmd = parser.parse("add append from temp where visible")

        assert cmd.append_mode is True
        assert cmd.source == 'temp'
        assert cmd.condition_tree is not None

    def test_parse_list_temp_sets_source(self):
        """Test that list temp sets source field"""
        parser = Parser()
        cmd = parser.parse("list temp")

        assert cmd.source == 'temp'
        assert cmd.target is None


class TestParserComplexScenarios:
    """Test complex parsing scenarios"""

    def test_parse_find_button_where_visible_and_enabled(self):
        """Test complex WHERE with AND"""
        parser = Parser()
        cmd = parser.parse("find button where visible and enabled")

        assert cmd.verb == 'find'
        assert cmd.target.element_type == 'button'
        assert cmd.condition_tree.type == ConditionType.COMPOUND

    def test_parse_add_from_candidates_where_type_equals_button(self):
        """Test add from candidates with condition"""
        parser = Parser()
        cmd = parser.parse('add from candidates where type="button"')

        assert cmd.verb == 'add'
        assert cmd.source == 'candidates'
        assert cmd.condition_tree.type == ConditionType.SIMPLE
        assert cmd.condition_tree.field == 'type'
        assert cmd.condition_tree.operator == Operator.EQUALS

    def test_parse_dot_find_with_complex_condition(self):
        """Test .find with complex condition"""
        parser = Parser()
        cmd = parser.parse(
            '.find where visible and text contains "Submit" and enabled')

        assert cmd.verb == 'find'
        assert cmd.is_refine is True
        assert cmd.condition_tree.type == ConditionType.COMPOUND
