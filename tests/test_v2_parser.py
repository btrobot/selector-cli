"""
Tests for ParserV2 - Extended syntax parsing
"""
import pytest
from selector_cli.parser.command import TargetType, Operator
from selector_cli_v2.v2.parser import ParserV2
from selector_cli_v2.v2.command import CommandV2


class TestParserV2DotFindSyntax:
    """Test .find syntax for refinement"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_find_basic(self):
        """Test: find button"""
        cmd = self.parser.parse("find button")

        assert isinstance(cmd, CommandV2)
        assert cmd.verb == "find"
        assert cmd.element_types == ["button"]
        assert cmd.variant is None  # No dot prefix
        assert cmd.mode == "overwrite"

    def test_find_multiple_types(self):
        """Test: find button, input, div"""
        cmd = self.parser.parse("find button, input, div")

        assert cmd.element_types == ["button", "input", "div"]

    def test_find_with_where(self):
        """Test: find div where role=\"button\""""
        cmd = self.parser.parse('find div where role="button"')

        assert cmd.element_types == ["div"]
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.type.name == "SIMPLE"
        assert cmd.condition_tree.field == "role"
        assert cmd.condition_tree.value == "button"

    def test_dot_find_refine(self):
        """Test: .find where visible"""
        cmd = self.parser.parse(".find where visible")

        assert cmd.verb == "find"
        assert cmd.variant == "refine"
        assert cmd.element_types is None
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.field == "visible"

    def test_dot_find_chained_condition(self):
        """Test: .find where enabled and visible"""
        cmd = self.parser.parse(".find where enabled and visible")

        assert cmd.variant == "refine"
        assert cmd.condition_tree.type.name == "COMPOUND"
        assert cmd.condition_tree.logic_op.name == "AND"

    def test_find_all_elements(self):
        """Test: find *"""
        cmd = self.parser.parse("find *")

        assert cmd.element_types == ["*"]


class TestParserV2AddSyntax:
    """Test add command with from <source> syntax"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_add_basic(self):
        """Test: add button"""
        cmd = self.parser.parse("add button")

        assert cmd.verb == "add"
        assert cmd.element_types == ["button"]
        assert cmd.source is None  # Will use convention (candidates)

    def test_add_from_temp(self):
        """Test: add from temp"""
        cmd = self.parser.parse("add from temp")

        assert cmd.source == "temp"
        assert cmd.element_types is None  # Add all from temp

    def test_add_from_candidates(self):
        """Test: add from candidates button"""
        cmd = self.parser.parse("add from candidates button")

        assert cmd.source == "candidates"
        assert cmd.element_types == ["button"]

    def test_add_from_workspace(self):
        """Test: add from workspace"""
        cmd = self.parser.parse("add from workspace")

        assert cmd.source == "workspace"

    def test_add_append(self):
        """Test: add append button"""
        cmd = self.parser.parse("add append button")

        assert cmd.mode == "append"
        assert cmd.element_types == ["button"]

    def test_add_with_where(self):
        """Test: add button where visible"""
        cmd = self.parser.parse("add button where visible")

        assert cmd.element_types == ["button"]
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.field == "visible"

    def test_add_multiple_types(self):
        """Test: add button, input, div"""
        cmd = self.parser.parse("add button, input, div")

        assert cmd.element_types == ["button", "input", "div"]


class TestParserV2ListSyntax:
    """Test list command with explicit source"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_list_default(self):
        """Test: list (defaults to workspace)"""
        cmd = self.parser.parse("list")

        assert cmd.verb == "list"
        assert cmd.source is None  # Uses convention (workspace)

    def test_list_candidates(self):
        """Test: list candidates"""
        cmd = self.parser.parse("list candidates")

        assert cmd.source == "candidates"

    def test_list_temp(self):
        """Test: list temp"""
        cmd = self.parser.parse("list temp")

        assert cmd.source == "temp"

    def test_list_workspace(self):
        """Test: list workspace"""
        cmd = self.parser.parse("list workspace")

        assert cmd.source == "workspace"

    def test_list_with_where(self):
        """Test: list where visible"""
        cmd = self.parser.parse("list where visible")

        assert cmd.condition_tree is not None
        assert cmd.condition_tree.field == "visible"

    def test_list_with_target_and_where(self):
        """Test: list button where text contains \"Submit\""""
        cmd = self.parser.parse('list button where text contains "Submit"')

        assert cmd.target.type == TargetType.ELEMENT_TYPE
        assert cmd.target.element_type == "button"
        assert cmd.condition_tree is not None
        assert cmd.condition_tree.operator == Operator.CONTAINS
        assert cmd.condition_tree.value == "Submit"


class TestParserV2ExportSyntax:
    """Test export command with from <source>"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_export_yaml(self):
        """Test: export yaml"""
        cmd = self.parser.parse("export yaml")

        assert cmd.verb == "export"
        assert cmd.argument == "yaml"
        assert cmd.source is None

    def test_export_yaml_with_file(self):
        """Test: export yaml > form.yaml"""
        cmd = self.parser.parse("export yaml > form.yaml")

        assert cmd.argument == "yaml:form.yaml"

    def test_export_from_temp(self):
        """Test: export yaml from temp"""
        cmd = self.parser.parse("export yaml from temp")

        assert cmd.argument == "yaml"
        assert cmd.source == "temp"

    def test_export_yaml_file_from_temp(self):
        """Test: export yaml > debug.yaml from temp"""
        cmd = self.parser.parse("export yaml > debug.yaml from temp")

        assert cmd.argument == "yaml:debug.yaml"
        assert cmd.source == "temp"


class TestParserV2ScanSyntax:
    """Test scan command with element types"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_scan_default(self):
        """Test: scan"""
        cmd = self.parser.parse("scan")

        assert cmd.verb == "scan"
        assert cmd.element_types is None

    def test_scan_with_types(self):
        """Test: scan button, input"""
        cmd = self.parser.parse("scan button, input")

        assert cmd.element_types == ["button", "input"]

    def test_scan_div(self):
        """Test: scan div"""
        cmd = self.parser.parse("scan div")

        assert cmd.element_types == ["div"]

    def test_scan_with_options(self):
        """Test: scan button --deep"""
        cmd = self.parser.parse("scan button --deep")

        assert cmd.element_types == ["button"]
        assert "deep" in cmd.options
        assert cmd.options["deep"] is True

    def test_scan_all(self):
        """Test: scan *"""
        cmd = self.parser.parse("scan *")

        assert cmd.element_types == ["*"]


class TestParserV2RemoveSyntax:
    """Test remove command with source"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_remove_basic(self):
        """Test: remove button"""
        cmd = self.parser.parse("remove button")

        assert cmd.verb == "remove"
        assert cmd.target.type == TargetType.ELEMENT_TYPE
        assert cmd.target.element_type == "button"

    def test_remove_from_temp(self):
        """Test: remove from temp"""
        cmd = self.parser.parse("remove from temp")

        assert cmd.source == "temp"

    def test_remove_with_where(self):
        """Test: remove button where not visible"""
        cmd = self.parser.parse("remove button where not visible")

        assert cmd.target.element_type == "button"
        assert cmd.condition_tree is not None


class TestParserV2RealWorldScenarios:
    """Test real-world usage scenarios"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_scan_add_workflow(self):
        """Test: scan -> add button -> list"""
        # scan
        scan_cmd = self.parser.parse("scan")
        assert scan_cmd.verb == "scan"

        # add button
        add_cmd = self.parser.parse("add button")
        assert add_cmd.verb == "add"
        assert add_cmd.element_types == ["button"]

        # list (default workspace)
        list_cmd = self.parser.parse("list")
        assert list_cmd.verb == "list"

    def test_find_role_button_workflow(self):
        """Test: find div where role=\"button\" -> list temp -> add from temp"""
        # find div where role="button"
        find_cmd = self.parser.parse('find div where role="button"')
        assert find_cmd.element_types == ["div"]
        assert find_cmd.condition_tree.field == "role"

        # list temp
        list_cmd = self.parser.parse("list temp")
        assert list_cmd.source == "temp"

        # add from temp
        add_cmd = self.parser.parse("add from temp")
        assert add_cmd.source == "temp"

    def test_chain_refine_commands(self):
        """Test: find div where role=\"button\" -> .find where visible -> .find where enabled"""
        # Initial find
        cmd1 = self.parser.parse('find div where role="button"')
        assert cmd1.variant is None

        # Refine with .find
        cmd2 = self.parser.parse(".find where visible")
        assert cmd2.variant == "refine"

        # Refine again
        cmd3 = self.parser.parse(".find where enabled")
        assert cmd3.variant == "refine"

    def test_complex_filter_scenario(self):
        """Test: add button where visible and enabled"""
        cmd = self.parser.parse("add button where visible and enabled")

        assert cmd.element_types == ["button"]
        assert cmd.condition_tree.type.name == "COMPOUND"
        assert cmd.condition_tree.logic_op.name == "AND"

    def test_export_debug_scenario(self):
        """Test: export yaml > debug.yaml from temp"""
        cmd = self.parser.parse("export yaml > debug.yaml from temp")

        assert cmd.argument == "yaml:debug.yaml"
        assert cmd.source == "temp"


class TestParserV2FallbackToV1:
    """Test that v2 parser falls back to v1 for unsupported commands"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_open_command(self):
        """Test: open https://example.com"""
        cmd = self.parser.parse("open https://example.com")

        assert cmd.verb == "open"
        assert cmd.argument == "https://example.com"
        assert isinstance(cmd, CommandV2)  # Should still return CommandV2

    def test_clear_command(self):
        """Test: clear"""
        cmd = self.parser.parse("clear")

        assert cmd.verb == "clear"

    def test_set_command(self):
        """Test: set variable = button"""
        cmd = self.parser.parse("set variable = button")

        assert cmd.verb == "set"
        assert cmd.target.type == TargetType.ELEMENT_TYPE


class TestParserV2ErrorCases:
    """Test error handling"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = ParserV2()

    def test_empty_command(self):
        """Test empty command"""
        with pytest.raises(ValueError, match="Empty command"):
            self.parser.parse("")

    def test_invalid_source(self):
        """Test invalid source name"""
        with pytest.raises(ValueError):
            self.parser.parse("add from invalid")

    def test_missing_target_after_from(self):
        """Test incomplete command"""
        with pytest.raises(ValueError):
            self.parser.parse("add from")
