"""
Parser for Selector CLI (Phase 1)
"""
from typing import List, Optional
from src.parser.lexer import Lexer, Token, TokenType
from src.parser.command import Command, Target, TargetType, Condition, Operator


class Parser:
    """Parse command strings into Command objects"""

    def __init__(self):
        self.lexer = Lexer()
        self.tokens: List[Token] = []
        self.position = 0

    def parse(self, command_str: str) -> Command:
        """Parse command string"""
        # Tokenize
        self.tokens = self.lexer.tokenize(command_str)
        self.position = 0

        # Empty command
        if self._current_token().type == TokenType.EOF:
            raise ValueError("Empty command")

        # Parse based on verb
        verb_token = self._current_token()

        if verb_token.type == TokenType.OPEN:
            return self._parse_open(command_str)
        elif verb_token.type == TokenType.SCAN:
            return self._parse_scan(command_str)
        elif verb_token.type == TokenType.ADD:
            return self._parse_add(command_str)
        elif verb_token.type == TokenType.REMOVE:
            return self._parse_remove(command_str)
        elif verb_token.type == TokenType.CLEAR:
            return self._parse_clear(command_str)
        elif verb_token.type == TokenType.LIST:
            return self._parse_list(command_str)
        elif verb_token.type == TokenType.SHOW:
            return self._parse_show(command_str)
        elif verb_token.type == TokenType.COUNT:
            return self._parse_count(command_str)
        elif verb_token.type in (TokenType.QUIT, TokenType.EXIT):
            return Command(verb='quit', raw=command_str)
        elif verb_token.type == TokenType.HELP:
            return self._parse_help(command_str)
        else:
            raise ValueError(f"Unknown command: {verb_token.value}")

    def _parse_open(self, raw: str) -> Command:
        """Parse: open <url>"""
        self._consume(TokenType.OPEN)

        # Get URL (could be string or identifier)
        url_token = self._current_token()
        if url_token.type == TokenType.STRING:
            url = url_token.value
            self._advance()
        elif url_token.type == TokenType.IDENTIFIER:
            # URL without quotes
            url = url_token.value
            self._advance()
            # Continue reading until EOF to get full URL
            while self._current_token().type not in (TokenType.EOF,):
                url += self._current_token().value
                self._advance()
        else:
            raise ValueError("Expected URL after 'open'")

        return Command(verb='open', argument=url, raw=raw)

    def _parse_scan(self, raw: str) -> Command:
        """Parse: scan"""
        self._consume(TokenType.SCAN)
        return Command(verb='scan', raw=raw)

    def _parse_add(self, raw: str) -> Command:
        """Parse: add <target> [where <condition>]"""
        self._consume(TokenType.ADD)

        # Parse target
        target = self._parse_target()

        # Parse optional WHERE clause
        condition = None
        if self._current_token().type == TokenType.WHERE:
            condition = self._parse_where_clause()

        return Command(verb='add', target=target, condition=condition, raw=raw)

    def _parse_remove(self, raw: str) -> Command:
        """Parse: remove <target> [where <condition>]"""
        self._consume(TokenType.REMOVE)

        # Parse target
        target = self._parse_target()

        # Parse optional WHERE clause
        condition = None
        if self._current_token().type == TokenType.WHERE:
            condition = self._parse_where_clause()

        return Command(verb='remove', target=target, condition=condition, raw=raw)

    def _parse_clear(self, raw: str) -> Command:
        """Parse: clear"""
        self._consume(TokenType.CLEAR)
        return Command(verb='clear', raw=raw)

    def _parse_list(self, raw: str) -> Command:
        """Parse: list [<target>] [where <condition>]"""
        self._consume(TokenType.LIST)

        # Optional target
        target = None
        if self._current_token().type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK, TokenType.ALL,
            TokenType.LBRACKET
        ):
            target = self._parse_target()

        # Optional WHERE clause
        condition = None
        if self._current_token().type == TokenType.WHERE:
            condition = self._parse_where_clause()

        return Command(verb='list', target=target, condition=condition, raw=raw)

    def _parse_show(self, raw: str) -> Command:
        """Parse: show [<target>]"""
        self._consume(TokenType.SHOW)

        # Optional target
        target = None
        if self._current_token().type == TokenType.LBRACKET:
            target = self._parse_target()

        return Command(verb='show', target=target, raw=raw)

    def _parse_count(self, raw: str) -> Command:
        """Parse: count"""
        self._consume(TokenType.COUNT)
        return Command(verb='count', raw=raw)

    def _parse_help(self, raw: str) -> Command:
        """Parse: help"""
        self._consume(TokenType.HELP)
        return Command(verb='help', raw=raw)

    def _parse_target(self) -> Target:
        """Parse target: element_type | [n] | [n,m,...] | all"""
        current = self._current_token()

        # Element type
        if current.type in (
            TokenType.INPUT, TokenType.BUTTON, TokenType.SELECT,
            TokenType.TEXTAREA, TokenType.LINK
        ):
            elem_type = current.value
            self._advance()
            return Target(type=TargetType.ELEMENT_TYPE, element_type=elem_type)

        # All
        if current.type == TokenType.ALL:
            self._advance()
            return Target(type=TargetType.ALL)

        # Index or indices
        if current.type == TokenType.LBRACKET:
            self._consume(TokenType.LBRACKET)

            indices = []
            # Read first number
            if self._current_token().type == TokenType.NUMBER:
                indices.append(int(self._current_token().value))
                self._advance()

                # Check for more indices
                while self._current_token().type == TokenType.COMMA:
                    self._consume(TokenType.COMMA)
                    if self._current_token().type == TokenType.NUMBER:
                        indices.append(int(self._current_token().value))
                        self._advance()

            self._consume(TokenType.RBRACKET)

            if len(indices) == 1:
                return Target(type=TargetType.INDEX, indices=indices)
            else:
                return Target(type=TargetType.INDICES, indices=indices)

        raise ValueError(f"Expected target, got {current.type}")

    def _parse_where_clause(self) -> Condition:
        """Parse: where <field> <op> <value>"""
        self._consume(TokenType.WHERE)

        # Field (identifier)
        if self._current_token().type != TokenType.IDENTIFIER:
            raise ValueError("Expected field name in WHERE clause")
        field = self._current_token().value
        self._advance()

        # Operator
        op_token = self._current_token()
        if op_token.type == TokenType.EQUALS:
            operator = Operator.EQUALS
        elif op_token.type == TokenType.NOT_EQUALS:
            operator = Operator.NOT_EQUALS
        else:
            raise ValueError(f"Expected operator, got {op_token.type}")
        self._advance()

        # Value
        value_token = self._current_token()
        if value_token.type == TokenType.STRING:
            value = value_token.value
        elif value_token.type == TokenType.NUMBER:
            value = int(value_token.value)
        elif value_token.type == TokenType.IDENTIFIER:
            value = value_token.value
        else:
            raise ValueError(f"Expected value, got {value_token.type}")
        self._advance()

        return Condition(field=field, operator=operator, value=value)

    def _current_token(self) -> Token:
        """Get current token"""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.position]

    def _advance(self):
        """Move to next token"""
        if self.position < len(self.tokens) - 1:
            self.position += 1

    def _consume(self, expected_type: TokenType):
        """Consume token of expected type"""
        if self._current_token().type != expected_type:
            raise ValueError(
                f"Expected {expected_type}, got {self._current_token().type}"
            )
        self._advance()
