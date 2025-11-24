"""
Tests for v2 bug fixes - BrowserManager.query_selector_all and Parser DIV token
"""
import pytest
from selector_cli.core.browser import BrowserManager
from selector_cli.parser.parser import Parser


class TestBrowserManagerQuerySelector:
    """Test BrowserManager.query_selector_all method"""

    def test_query_selector_all_method_exists(self):
        """Test that query_selector_all method exists"""
        bm = BrowserManager()
        assert hasattr(bm, 'query_selector_all')

    def test_query_selector_all_signature(self):
        """Test query_selector_all has correct signature"""
        import inspect
        bm = BrowserManager()
        sig = inspect.signature(bm.query_selector_all)
        params = list(sig.parameters.keys())
        assert 'selector' in params


class TestParserFindDiv:
    """Test Parser can parse 'find div' command"""

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_parse_find_div(self, parser):
        """Test parsing 'find div'"""
        cmd = parser.parse("find div")
        assert cmd.verb == 'find'
        assert cmd.target is not None
        assert cmd.target.type.value == 1  # ELEMENT_TYPE
        assert cmd.target.element_type == 'div'

    def test_parse_find_button(self, parser):
        """Test parsing 'find button'"""
        cmd = parser.parse("find button")
        assert cmd.verb == 'find'
        assert cmd.target is not None
        assert cmd.target.element_type == 'button'

    def test_parse_find_input(self, parser):
        """Test parsing 'find input'"""
        cmd = parser.parse("find input")
        assert cmd.verb == 'find'
        assert cmd.target is not None
        assert cmd.target.element_type == 'input'

    def test_parse_find_with_where(self, parser):
        """Test parsing 'find div where visible'"""
        cmd = parser.parse("find div where visible")
        assert cmd.verb == 'find'
        assert cmd.target.element_type == 'div'
        assert cmd.condition_tree is not None

    def test_parse_dot_find_refine(self, parser):
        """Test parsing '.find where visible'"""
        cmd = parser.parse(".find where visible")
        assert cmd.verb == 'find'
        assert cmd.is_refine is True
        assert cmd.condition_tree is not None
        assert cmd.target is None  # Refine doesn't need target

    def test_parse_find_multiple_element_types(self, parser):
        """Test parsing various element types"""
        test_cases = [
            ("find div", "div"),
            ("find button", "button"),
            ("find input", "input"),
            ("find select", "select"),
            ("find textarea", "textarea"),
        ]

        for command_str, expected_type in test_cases:
            cmd = parser.parse(command_str)
            assert cmd.verb == 'find'
            assert cmd.target.element_type == expected_type
