import pytest
from selector_cli.parser.command import Target, TargetType, Condition, Operator
from selector_cli_v2.v2.command import CommandV2


class TestCommandV2Structure:
    """Test CommandV2 structure and fields"""

    def test_basic_command_creation(self):
        """Test creating a basic CommandV2"""
        cmd = CommandV2(verb="find", raw="find button")

        assert cmd.verb == "find"
        assert cmd.raw == "find button"
        assert cmd.element_types is None
        assert cmd.source is None
        assert cmd.mode == "overwrite"
        assert cmd.variant is None
        assert cmd.options == {}

    def test_command_with_element_types(self):
        """Test command with element types"""
        cmd = CommandV2(
            verb="find",
            element_types=["button", "input", "div"],
            raw="find button, input, div"
        )

        assert cmd.element_types == ["button", "input", "div"]

    def test_command_with_source(self):
        """Test command with source specification"""
        cmd = CommandV2(
            verb="add",
            source="temp",
            raw="add from temp"
        )

        assert cmd.source == "temp"

    def test_command_in_append_mode(self):
        """Test command in append mode"""
        cmd = CommandV2(
            verb="add",
            mode="append",
            raw="add append button"
        )

        assert cmd.mode == "append"
        assert cmd.is_append_mode() is True
        assert cmd.is_overwrite_mode() is False

    def test_refine_command(self):
        """Test .find refine command"""
        cmd = CommandV2(
            verb="find",
            variant="refine",
            raw=".find where visible"
        )

        assert cmd.variant == "refine"
        assert cmd.is_refine_command() is True


class TestCommandV2Conventions:
    """Test convention over configuration logic"""

    def test_get_source_layer_defaults(self):
        """Test default source layer based on conventions"""
        # .find command defaults to temp
        cmd = CommandV2(verb="find", variant="refine", raw=".find")
        assert cmd.get_source_layer() == "temp"

        # add command defaults to candidates
        cmd = CommandV2(verb="add", raw="add button")
        assert cmd.get_source_layer() == "candidates"

        # Explicit source overrides convention
        cmd = CommandV2(verb="add", source="workspace", raw="add from workspace")
        assert cmd.get_source_layer() == "workspace"

    def test_get_target_layer_defaults(self):
        """Test default target layer based on conventions"""
        # list, preview, remove, export default to workspace
        assert CommandV2(verb="list", raw="list").get_target_layer() == "workspace"
        assert CommandV2(verb="preview", raw="preview").get_target_layer() == "workspace"
        assert CommandV2(verb="remove", raw="remove button").get_target_layer() == "workspace"
        assert CommandV2(verb="export", raw="export yaml").get_target_layer() == "workspace"

        # find defaults to temp
        assert CommandV2(verb="find", raw="find button").get_target_layer() == "temp"

        # add defaults to workspace
        assert CommandV2(verb="add", raw="add button").get_target_layer() == "workspace"

        # scan defaults to candidates
        assert CommandV2(verb="scan", raw="scan").get_target_layer() == "candidates"


class TestCommandV2WithTarget:
    """Test CommandV2 with target specification"""

    def test_command_with_target(self):
        """Test command with target"""
        target = Target(
            type=TargetType.ELEMENT_TYPE,
            element_type="button"
        )
        cmd = CommandV2(
            verb="add",
            target=target,
            raw="add button"
        )

        assert cmd.target.type == TargetType.ELEMENT_TYPE
        assert cmd.target.element_type == "button"

    def test_command_with_index_target(self):
        """Test command with index target"""
        target = Target(
            type=TargetType.INDEX,
            indices=[5]
        )
        cmd = CommandV2(
            verb="preview",
            target=target,
            raw="preview 5"
        )

        assert cmd.target.type == TargetType.INDEX
        assert cmd.target.indices == [5]


class TestCommandV2WithConditions:
    """Test CommandV2 with WHERE conditions"""

    def test_command_with_simple_condition(self):
        """Test command with simple condition"""
        condition = Condition(
            field="visible",
            operator=Operator.EQUALS,
            value=True
        )
        cmd = CommandV2(
            verb="add",
            condition=condition,
            raw="add button where visible"
        )

        assert cmd.condition is not None
        assert cmd.condition.field == "visible"
        assert cmd.condition.operator == Operator.EQUALS
        assert cmd.condition.value is True
        assert cmd.has_condition() is True

    def test_command_without_condition(self):
        """Test command without condition"""
        cmd = CommandV2(verb="list", raw="list")
        assert cmd.condition is None
        assert cmd.has_condition() is False


class TestCommandV2Options:
    """Test CommandV2 options and flags"""

    def test_command_with_options(self):
        """Test command with options"""
        cmd = CommandV2(
            verb="find",
            options={"timeout": 5, "visible_only": True},
            raw="find button --timeout 5 --visible-only"
        )

        assert cmd.options["timeout"] == 5
        assert cmd.options["visible_only"] is True

    def test_command_with_empty_options(self):
        """Test command with empty options"""
        cmd = CommandV2(verb="scan", raw="scan")
        assert cmd.options == {}


class TestCommandV2Serialization:
    """Test CommandV2 serialization"""

    def test_to_dict_basic(self):
        """Test basic command to_dict"""
        cmd = CommandV2(
            verb="find",
            element_types=["button"],
            raw="find button"
        )

        result = cmd.to_dict()

        assert result["verb"] == "find"
        assert result["element_types"] == ["button"]
        assert result["source"] is None
        assert result["mode"] == "overwrite"
        assert result["variant"] is None
        assert result["options"] == {}
        assert result["raw"] == "find button"

    def test_to_dict_with_target(self):
        """Test command to_dict with target"""
        target = Target(
            type=TargetType.ELEMENT_TYPE,
            element_type="input"
        )
        cmd = CommandV2(
            verb="add",
            target=target,
            raw="add input"
        )

        result = cmd.to_dict()

        assert "target" in result
        assert result["target"]["element_type"] == "input"
        assert result["target"]["type"] == "ELEMENT_TYPE"

    def test_to_dict_with_condition(self):
        """Test command to_dict with condition"""
        condition = Condition(
            field="role",
            operator=Operator.EQUALS,
            value="button"
        )
        cmd = CommandV2(
            verb="find",
            element_types=["div"],
            condition=condition,
            raw="find div where role=\"button\""
        )

        result = cmd.to_dict()

        assert "condition" in result
        assert result["condition"]["field"] == "role"
        assert result["condition"]["operator"] == "EQUALS"
        assert result["condition"]["value"] == "button"


class TestCommandV2RealScenarios:
    """Test CommandV2 with real-world scenarios"""

    def test_find_role_button_scenario(self):
        """Test: find div where role=\"button\""""
        condition = Condition(
            field="role",
            operator=Operator.EQUALS,
            value="button"
        )
        cmd = CommandV2(
            verb="find",
            element_types=["div"],
            condition=condition,
            raw="find div where role=\"button\""
        )

        assert cmd.get_target_layer() == "temp"
        assert cmd.source is None  # Not from temp

    def test_refine_visible_scenario(self):
        """Test: .find where visible"""
        condition = Condition(
            field="visible",
            operator=Operator.EQUALS,
            value=True
        )
        cmd = CommandV2(
            verb="find",
            variant="refine",
            condition=condition,
            raw=".find where visible"
        )

        assert cmd.is_refine_command() is True
        assert cmd.get_source_layer() == "temp"

    def test_add_from_temp_scenario(self):
        """Test: add from temp"""
        cmd = CommandV2(
            verb="add",
            source="temp",
            raw="add from temp"
        )

        assert cmd.source == "temp"
        assert cmd.get_target_layer() == "workspace"

    def test_scan_deep_scenario(self):
        """Test: scan --deep"""
        cmd = CommandV2(
            verb="scan",
            options={"deep": True, "types": ["input", "button"]},
            raw="scan --deep input, button"
        )

        assert cmd.options["deep"] is True
        assert cmd.options["types"] == ["input", "button"]
        assert cmd.get_target_layer() == "candidates"

    def test_workspace_list_scenario(self):
        """Test: list (default to workspace)"""
        cmd = CommandV2(
            verb="list",
            raw="list"
        )

        assert cmd.get_target_layer() == "workspace"
        assert cmd.source is None

    def test_append_scenario(self):
        """Test: find append div"""
        target = Target(
            type=TargetType.ELEMENT_TYPE,
            element_type="div"
        )
        cmd = CommandV2(
            verb="find",
            target=target,
            mode="append",
            raw="find append div"
        )

        assert cmd.mode == "append"
        assert cmd.is_append_mode() is True
        assert cmd.get_target_layer() == "temp"
