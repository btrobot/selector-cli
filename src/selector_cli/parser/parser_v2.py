"""
V2 Parser for extended syntax (.find, from <source>, append, etc.)
"""
from typing import Optional, List, Any
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from selector_cli.parser.parser import Parser as V1Parser
from selector_cli.parser.lexer import Lexer, Token, TokenType
from selector_cli.parser.command import (
    Target, TargetType, Condition, Operator,
    ConditionNode, ConditionType, LogicOp
)
from selector_cli.parser.command_v2 import CommandV2


class ParserV2(V1Parser):
    """V2 parser with extended syntax support"""

    def __init__(self):
        super().__init__()
        self._dot_prefix = False  # Track if this is a .find command

    def parse(self, command_str: str) -> CommandV2:
        """Parse command string with v2 extensions"""
        # Check for . prefix (refine command)
        stripped = command_str.strip()
        self._dot_prefix = stripped.startswith('.')

        # Use v1 parser to tokenize
        self.tokens = self.lexer.tokenize(command_str)
        self.position = 0

        # Empty command
        if self._current_token().type == TokenType.EOF:
            raise ValueError("Empty command")

        # If it starts with dot, consume it
        if self._dot_prefix and self._current_token().value == '.':
            self._consume(TokenType.DOT)

        # Parse based on verb
        verb_token = self._current_token()

        # Route to appropriate parser
        if verb_token.type == TokenType.FIND:
            return self._parse_find_v2(command_str)
        elif verb_token.type == TokenType.ADD:
            return self._parse_add_v2(command_str)
        elif verb_token.type == TokenType.REMOVE:
            return self._parse_remove_v2(command_str)
        elif verb_token.type == TokenType.LIST:
            return self._parse_list_v2(command_str)
        elif verb_token.type == TokenType.PREVIEW:
            return self._parse_preview_v2(command_str)
        elif verb_token.type == TokenType.EXPORT:
            return self._parse_export_v2(command_str)
        elif verb_token.type == TokenType.SCAN:
            return self._parse_scan_v2(command_str)
        else:
            # Fall back to v1 parser for other commands
            v1_cmd = super().parse(command_str)
            return CommandV2(
                verb=v1_cmd.verb,
                target=v1_cmd.target,
                condition=v1_cmd.condition,
                condition_tree=v1_cmd.condition_tree,
                argument=v1_cmd.argument,
                raw=v1_cmd.raw
            )

    # =========================================================================
    # V2 Command Parsers
    # =========================================================================

    def _parse_find_v2(self, raw: str) -> CommandV2:
        """Parse: find [element_types] [where <condition>]"""
        self._consume(TokenType.FIND)

        # Parse element types (comma-separated list)
        element_types: Optional[List[str]] = None
        if self._current_token().type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER,
            TokenType.ALL, TokenType.DIV
        ):
            element_types = self._parse_element_types()

        # Parse optional WHERE clause
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        # Determine command properties
        variant = "refine" if self._dot_prefix else None
        mode = "overwrite"  # Default, unless append is specified

        return CommandV2(
            verb="find",
            element_types=element_types,
            condition_tree=condition_tree,
            mode=mode,
            variant=variant,
            raw=raw
        )

    def _parse_add_v2(self, raw: str) -> CommandV2:
        """Parse: add [from <source>] <target> [where <condition>]"""
        self._consume(TokenType.ADD)

        # Check for "append" mode
        mode = "overwrite"
        if self._current_token().type == TokenType.APPEND:
            self._consume(TokenType.APPEND)
            mode = "append"

        # Check for "from <source>"
        source = None
        element_types = None

        if self._current_token().type == TokenType.FROM:
            self._consume(TokenType.FROM)
            # Next token should be source name (candidates, temp, workspace)
            source_token = self._current_token()
            if source_token.type == TokenType.IDENTIFIER and source_token.value in (
                "candidates", "temp", "workspace"
            ):
                source = source_token.value
                self._advance()
            else:
                raise ValueError(f"Expected source name (candidates/temp/workspace), got {source_token.value}")

        # Parse target (element types)
        target = None
        if self._current_token().type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER, TokenType.ALL
        ):
            # Could be a single element type or comma-separated list
            element_types = self._parse_element_types()
            # Also parse as target
            target = Target(type=TargetType.ELEMENT_TYPE, element_type=element_types[0])

        # Parse optional WHERE clause
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return CommandV2(
            verb="add",
            element_types=element_types,
            source=source,
            target=target,
            condition_tree=condition_tree,
            mode=mode,
            raw=raw
        )

    def _parse_remove_v2(self, raw: str) -> CommandV2:
        """Parse: remove [from <source>] <target> [where <condition>]"""
        self._consume(TokenType.REMOVE)

        # Check for "from <source>" (workspace is default via convention)
        source = None
        if self._current_token().type == TokenType.FROM:
            self._consume(TokenType.FROM)
            source_token = self._current_token()
            if source_token.type == TokenType.IDENTIFIER and source_token.value in (
                "candidates", "temp", "workspace"
            ):
                source = source_token.value
                self._advance()
            else:
                raise ValueError(f"Expected source name (candidates/temp/workspace), got {source_token.value}")

        # Parse target
        target = None
        if self._current_token().type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER, TokenType.ALL
        ):
            target = self._parse_target()

        # Parse optional WHERE clause
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return CommandV2(
            verb="remove",
            target=target,
            source=source,
            condition_tree=condition_tree,
            raw=raw
        )

    def _parse_list_v2(self, raw: str) -> CommandV2:
        """Parse: list [candidates|temp|workspace|target] [where <condition>]"""
        self._consume(TokenType.LIST)

        # Check for explicit source or target
        source = None
        target = None
        source_token = self._current_token()

        # Check if it's a source name (candidates/temp/workspace)
        if source_token.type == TokenType.IDENTIFIER and source_token.value in (
            "candidates", "temp", "workspace"
        ):
            source = source_token.value
            self._advance()
        # Check if it's a target (element type or index)
        elif source_token.type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.DIV, TokenType.ALL
        ):
            target = self._parse_target()

        # Parse optional WHERE clause
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return CommandV2(
            verb="list",
            source=source,
            target=target,
            condition_tree=condition_tree,
            raw=raw
        )

    def _parse_preview_v2(self, raw: str) -> CommandV2:
        """Parse: preview [candidates|temp|workspace]"""
        self._consume(TokenType.PREVIEW)

        # Check for explicit source
        source = None
        source_token = self._current_token()
        if source_token.type == TokenType.IDENTIFIER and source_token.value in (
            "candidates", "temp", "workspace"
        ):
            source = source_token.value
            self._advance()

        return CommandV2(
            verb="preview",
            source=source,
            raw=raw
        )

    def _parse_export_v2(self, raw: str) -> CommandV2:
        """Parse: export <format> [> <filename>] [from <source>]"""
        self._consume(TokenType.EXPORT)

        # Parse format and filename (from v1)
        format_token = self._current_token()
        valid_formats = (
            TokenType.PLAYWRIGHT, TokenType.SELENIUM, TokenType.PUPPETEER,
            TokenType.JSON, TokenType.CSV, TokenType.YAML
        )

        if format_token.type not in valid_formats:
            raise ValueError(f"Expected export format, got {format_token.value}")

        export_format = format_token.value
        self._advance()

        # Check for > filename
        filename = None
        if self._current_token().type == TokenType.GT:
            self._consume(TokenType.GT)
            filename_token = self._current_token()
            if filename_token.type in (TokenType.IDENTIFIER, TokenType.STRING):
                filename = filename_token.value
                self._advance()
                # Read rest of filename
                while self._current_token().type not in (TokenType.EOF, TokenType.FROM):
                    filename += self._current_token().value
                    self._advance()

        # Check for from <source>
        source = None
        if self._current_token().type == TokenType.FROM:
            self._consume(TokenType.FROM)
            source_token = self._current_token()
            if source_token.type == TokenType.IDENTIFIER and source_token.value in (
                "candidates", "temp", "workspace"
            ):
                source = source_token.value
                self._advance()

        # Build argument
        if filename:
            argument = f"{export_format}:{filename}"
        else:
            argument = export_format

        return CommandV2(
            verb="export",
            argument=argument,
            source=source,
            raw=raw
        )

    def _parse_scan_v2(self, raw: str) -> CommandV2:
        """Parse: scan [element_types] [--deep] [--types type1,type2]"""
        self._consume(TokenType.SCAN)

        # Parse element types (comma-separated list)
        element_types = None
        if self._current_token().type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER,
            TokenType.ALL, TokenType.DIV
        ):
            element_types = self._parse_element_types()

        # Parse options (Phase 2: --deep, --types, etc.)
        options = {}
        while self._current_token().type == TokenType.DOUBLE_DASH:
            self._consume(TokenType.DOUBLE_DASH)
            option_token = self._current_token()
            if option_token.type == TokenType.IDENTIFIER:
                option_name = option_token.value
                self._advance()

                # Check for = value
                if self._current_token().type == TokenType.EQUALS:
                    self._consume(TokenType.EQUALS)
                    option_value = self._parse_value()
                    options[option_name] = option_value
                else:
                    # Boolean flag
                    options[option_name] = True

        return CommandV2(
            verb="scan",
            element_types=element_types,
            options=options,
            raw=raw
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _parse_element_types(self) -> List[str]:
        """Parse comma-separated element types: button, input, div, ..."""
        types: List[str] = []

        # Parse first type
        current = self._current_token()
        if current.type == TokenType.ALL:
            types.append("*")
            self._advance()
        elif current.type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER,
            TokenType.DIV
        ):
            types.append(current.value)
            self._advance()
        else:
            raise ValueError(f"Expected element type, got {current.value}")

        # Parse additional types separated by commas
        while self._current_token().type == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            current = self._current_token()
            if current.type == TokenType.ALL:
                types.append("*")
                self._advance()
            elif current.type in (
                TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
                TokenType.TEXTAREA, TokenType.LINK, TokenType.IDENTIFIER,
                TokenType.DIV
            ):
                types.append(current.value)
                self._advance()
            else:
                raise ValueError(f"Expected element type after comma, got {current.value}")

        return types

    # Override to expose helper methods to V2
    def _parse_where_clause_v2(self) -> ConditionNode:
        """Expose parent method"""
        return super()._parse_where_clause_v2()

    def _parse_value(self) -> Any:
        """Expose parent method"""
        return super()._parse_value()
