"""
Parser for Selector CLI (Phase 2)
"""
from typing import List, Optional, Any
from src.parser.lexer import Lexer, Token, TokenType
from src.parser.command import (
    Command, Target, TargetType,
    Condition, Operator,  # Phase 1
    ConditionNode, ConditionType, LogicOp  # Phase 2
)


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
        elif verb_token.type == TokenType.EXPORT:
            return self._parse_export(command_str)
        elif verb_token.type == TokenType.SAVE:
            return self._parse_save(command_str)
        elif verb_token.type == TokenType.LOAD:
            return self._parse_load(command_str)
        elif verb_token.type == TokenType.SAVED:
            return self._parse_saved(command_str)
        elif verb_token.type == TokenType.DELETE:
            return self._parse_delete(command_str)
        elif verb_token.type == TokenType.SET:
            return self._parse_set(command_str)
        elif verb_token.type == TokenType.VARS:
            return self._parse_vars(command_str)
        elif verb_token.type == TokenType.MACRO:
            return self._parse_macro(command_str)
        elif verb_token.type == TokenType.RUN:
            return self._parse_run(command_str)
        elif verb_token.type == TokenType.MACROS:
            return self._parse_macros(command_str)
        elif verb_token.type == TokenType.EXEC:
            return self._parse_exec(command_str)
        elif verb_token.type == TokenType.HIGHLIGHT:
            return self._parse_highlight(command_str)
        elif verb_token.type == TokenType.UNHIGHLIGHT:
            return self._parse_unhighlight(command_str)
        elif verb_token.type == TokenType.UNION:
            return self._parse_union(command_str)
        elif verb_token.type == TokenType.INTERSECT:
            return self._parse_intersect(command_str)
        elif verb_token.type == TokenType.DIFFERENCE:
            return self._parse_difference(command_str)
        elif verb_token.type == TokenType.UNIQUE:
            return self._parse_unique(command_str)
        elif verb_token.type == TokenType.HISTORY:
            return self._parse_history(command_str)
        elif verb_token.type == TokenType.BANG:
            return self._parse_bang(command_str)
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

        # Parse optional WHERE clause (Phase 2 - complex conditions)
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return Command(verb='add', target=target, condition_tree=condition_tree, raw=raw)

    def _parse_remove(self, raw: str) -> Command:
        """Parse: remove <target> [where <condition>]"""
        self._consume(TokenType.REMOVE)

        # Parse target
        target = self._parse_target()

        # Parse optional WHERE clause (Phase 2)
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return Command(verb='remove', target=target, condition_tree=condition_tree, raw=raw)

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

        # Optional WHERE clause (Phase 2)
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return Command(verb='list', target=target, condition_tree=condition_tree, raw=raw)

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

    def _parse_export(self, raw: str) -> Command:
        """Parse: export <format> [> <filename>]"""
        self._consume(TokenType.EXPORT)

        # Get format
        format_token = self._current_token()
        valid_formats = (
            TokenType.PLAYWRIGHT, TokenType.SELENIUM, TokenType.PUPPETEER,
            TokenType.JSON, TokenType.CSV, TokenType.YAML
        )

        if format_token.type not in valid_formats:
            raise ValueError(
                f"Expected export format (playwright/selenium/puppeteer/json/csv/yaml), "
                f"got {format_token.value}"
            )

        export_format = format_token.value
        self._advance()

        # Check for file redirection: > filename
        filename = None
        if self._current_token().type == TokenType.GT:
            self._consume(TokenType.GT)

            # Get filename
            filename_token = self._current_token()
            if filename_token.type in (TokenType.IDENTIFIER, TokenType.STRING):
                filename = filename_token.value
                self._advance()

                # Continue reading to get full filename (may have dots, paths, etc.)
                while self._current_token().type not in (TokenType.EOF,):
                    if self._current_token().value in (' ', '\t'):
                        self._advance()
                        break
                    filename += self._current_token().value
                    self._advance()
            else:
                raise ValueError("Expected filename after '>'")

        # Store format and filename as argument (format:filename or just format)
        if filename:
            argument = f"{export_format}:{filename}"
        else:
            argument = export_format

        return Command(verb='export', argument=argument, raw=raw)

    # ========== Phase 4: Persistence Commands ==========

    def _parse_save(self, raw: str) -> Command:
        """Parse: save <name>"""
        self._consume(TokenType.SAVE)

        # Get collection name
        name_token = self._current_token()
        if name_token.type in (TokenType.STRING, TokenType.IDENTIFIER):
            name = name_token.value
            self._advance()
        else:
            raise ValueError("Expected collection name after 'save'")

        return Command(verb='save', argument=name, raw=raw)

    def _parse_load(self, raw: str) -> Command:
        """Parse: load <name>"""
        self._consume(TokenType.LOAD)

        # Get collection name
        name_token = self._current_token()
        if name_token.type in (TokenType.STRING, TokenType.IDENTIFIER):
            name = name_token.value
            self._advance()
        else:
            raise ValueError("Expected collection name after 'load'")

        return Command(verb='load', argument=name, raw=raw)

    def _parse_saved(self, raw: str) -> Command:
        """Parse: saved"""
        self._consume(TokenType.SAVED)
        return Command(verb='saved', raw=raw)

    def _parse_delete(self, raw: str) -> Command:
        """Parse: delete <name>"""
        self._consume(TokenType.DELETE)

        # Get collection name
        name_token = self._current_token()
        if name_token.type in (TokenType.STRING, TokenType.IDENTIFIER):
            name = name_token.value
            self._advance()
        else:
            raise ValueError("Expected collection name after 'delete'")

        return Command(verb='delete', argument=name, raw=raw)

    def _parse_set(self, raw: str) -> Command:
        """Parse: set <name> = <value>"""
        self._consume(TokenType.SET)

        # Get variable name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected variable name after 'set'")
        var_name = name_token.value
        self._advance()

        # Expect =
        self._consume(TokenType.EQUALS)

        # Get value
        value = self._parse_value()

        # Store as "name=value" in argument
        return Command(verb='set', argument=f"{var_name}={value}", raw=raw)

    def _parse_vars(self, raw: str) -> Command:
        """Parse: vars"""
        self._consume(TokenType.VARS)
        return Command(verb='vars', raw=raw)

    def _parse_macro(self, raw: str) -> Command:
        """Parse: macro <name> <command>"""
        self._consume(TokenType.MACRO)

        # Get macro name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected macro name after 'macro'")
        macro_name = name_token.value
        self._advance()

        # Get rest of line as macro command (preserve original)
        # Find position after macro name in original string
        macro_prefix = f"macro {macro_name}"
        macro_start = raw.find(macro_prefix)
        if macro_start >= 0:
            macro_command = raw[macro_start + len(macro_prefix):].strip()
        else:
            # Fallback: reconstruct from tokens
            command_parts = []
            while self._current_token().type != TokenType.EOF:
                token = self._current_token()
                # Preserve quotes for strings
                if token.type == TokenType.STRING:
                    command_parts.append(f'"{token.value}"')
                else:
                    command_parts.append(token.value)
                self._advance()
            macro_command = " ".join(command_parts)

        if not macro_command:
            raise ValueError("Macro must contain at least one command")

        # Store as "name:command" in argument
        return Command(verb='macro', argument=f"{macro_name}:{macro_command}", raw=raw)

    def _parse_run(self, raw: str) -> Command:
        """Parse: run <macro_name>"""
        self._consume(TokenType.RUN)

        # Get macro name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected macro name after 'run'")
        macro_name = name_token.value
        self._advance()

        return Command(verb='run', argument=macro_name, raw=raw)

    def _parse_macros(self, raw: str) -> Command:
        """Parse: macros"""
        self._consume(TokenType.MACROS)
        return Command(verb='macros', raw=raw)

    def _parse_exec(self, raw: str) -> Command:
        """Parse: exec <filepath>"""
        self._consume(TokenType.EXEC)

        # Get filepath (could be string or identifier)
        filepath_token = self._current_token()
        if filepath_token.type in (TokenType.STRING, TokenType.IDENTIFIER):
            filepath = filepath_token.value
            self._advance()

            # Continue reading to get full path
            while self._current_token().type not in (TokenType.EOF,):
                filepath += self._current_token().value
                self._advance()
        else:
            raise ValueError("Expected filepath after 'exec'")

        return Command(verb='exec', argument=filepath, raw=raw)

    def _parse_highlight(self, raw: str) -> Command:
        """Parse: highlight [<target>] [where <condition>]"""
        self._consume(TokenType.HIGHLIGHT)

        # Check if there's a target (optional)
        # If next token is EOF, highlight current collection
        if self._current_token().type == TokenType.EOF:
            return Command(verb='highlight', raw=raw)

        # Try to parse target
        target = None
        try:
            target = self._parse_target()
        except ValueError:
            # No target, highlight current collection
            return Command(verb='highlight', raw=raw)

        # Parse optional WHERE clause
        condition_tree = None
        if self._current_token().type == TokenType.WHERE:
            condition_tree = self._parse_where_clause_v2()

        return Command(verb='highlight', target=target, condition_tree=condition_tree, raw=raw)

    def _parse_unhighlight(self, raw: str) -> Command:
        """Parse: unhighlight"""
        self._consume(TokenType.UNHIGHLIGHT)
        return Command(verb='unhighlight', raw=raw)

    def _parse_union(self, raw: str) -> Command:
        """Parse: union <collection_name>"""
        self._consume(TokenType.UNION)

        # Get collection name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected collection name after 'union'")

        collection_name = name_token.value
        self._advance()

        return Command(verb='union', argument=collection_name, raw=raw)

    def _parse_intersect(self, raw: str) -> Command:
        """Parse: intersect <collection_name>"""
        self._consume(TokenType.INTERSECT)

        # Get collection name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected collection name after 'intersect'")

        collection_name = name_token.value
        self._advance()

        return Command(verb='intersect', argument=collection_name, raw=raw)

    def _parse_difference(self, raw: str) -> Command:
        """Parse: difference <collection_name>"""
        self._consume(TokenType.DIFFERENCE)

        # Get collection name
        name_token = self._current_token()
        if name_token.type != TokenType.IDENTIFIER:
            raise ValueError("Expected collection name after 'difference'")

        collection_name = name_token.value
        self._advance()

        return Command(verb='difference', argument=collection_name, raw=raw)

    def _parse_unique(self, raw: str) -> Command:
        """Parse: unique"""
        self._consume(TokenType.UNIQUE)
        return Command(verb='unique', raw=raw)

    def _parse_history(self, raw: str) -> Command:
        """Parse: history [n]"""
        self._consume(TokenType.HISTORY)

        # Check for optional number argument
        if self._current_token().type == TokenType.NUMBER:
            count = int(self._current_token().value)
            self._advance()
            return Command(verb='history', argument=str(count), raw=raw)

        return Command(verb='history', raw=raw)

    def _parse_bang(self, raw: str) -> Command:
        """Parse: !n or !!"""
        self._consume(TokenType.BANG)

        # Check next token
        next_token = self._current_token()

        if next_token.type == TokenType.BANG:
            # !! - execute last command
            self._advance()
            return Command(verb='bang_last', raw=raw)
        elif next_token.type == TokenType.NUMBER:
            # !n - execute command at index n
            index = int(next_token.value)
            self._advance()
            return Command(verb='bang_n', argument=str(index), raw=raw)
        else:
            raise ValueError("Expected number or '!' after '!'")


    def _parse_target(self) -> Target:
        """Parse target: element_type | [indices/range] | all"""
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

        # Index, indices, or range: [n], [n,m,...], [n-m], [n,m-p,q]
        if current.type == TokenType.LBRACKET:
            self._consume(TokenType.LBRACKET)

            indices = []

            while self._current_token().type != TokenType.RBRACKET:
                # Parse number
                if self._current_token().type == TokenType.NUMBER:
                    start = int(self._current_token().value)
                    self._advance()

                    # Check for range (dash)
                    if self._current_token().type == TokenType.DASH:
                        self._consume(TokenType.DASH)
                        if self._current_token().type == TokenType.NUMBER:
                            end = int(self._current_token().value)
                            self._advance()
                            # Expand range to indices
                            indices.extend(range(start, end + 1))
                        else:
                            raise ValueError("Expected number after -")
                    else:
                        # Single index
                        indices.append(start)

                    # Check for comma
                    if self._current_token().type == TokenType.COMMA:
                        self._consume(TokenType.COMMA)

            self._consume(TokenType.RBRACKET)

            if len(indices) == 1:
                return Target(type=TargetType.INDEX, indices=indices)
            else:
                return Target(type=TargetType.INDICES, indices=indices)

        raise ValueError(f"Expected target, got {current.type}")

    # ========== Phase 2: Complex WHERE Clause Parsing ==========

    def _parse_where_clause_v2(self) -> ConditionNode:
        """Parse complex WHERE clause with and/or/not and parentheses

        Grammar (with operator precedence):
            condition = or_condition
            or_condition = and_condition ('or' and_condition)*
            and_condition = not_condition ('and' not_condition)*
            not_condition = 'not' not_condition | primary_condition
            primary_condition = '(' condition ')' | simple_condition

        Operator precedence (high to low):
            1. Parentheses ()
            2. NOT
            3. AND
            4. OR
        """
        self._consume(TokenType.WHERE)
        return self._parse_or_condition()

    def _parse_or_condition(self) -> ConditionNode:
        """Parse OR expressions (lowest precedence)"""
        left = self._parse_and_condition()

        while self._current_token().type == TokenType.OR:
            self._advance()
            right = self._parse_and_condition()
            left = ConditionNode(
                type=ConditionType.COMPOUND,
                left=left,
                right=right,
                logic_op=LogicOp.OR
            )

        return left

    def _parse_and_condition(self) -> ConditionNode:
        """Parse AND expressions (higher precedence than OR)"""
        left = self._parse_not_condition()

        while self._current_token().type == TokenType.AND:
            self._advance()
            right = self._parse_not_condition()
            left = ConditionNode(
                type=ConditionType.COMPOUND,
                left=left,
                right=right,
                logic_op=LogicOp.AND
            )

        return left

    def _parse_not_condition(self) -> ConditionNode:
        """Parse NOT expressions (highest precedence among logic ops)"""
        if self._current_token().type == TokenType.NOT:
            self._advance()
            operand = self._parse_not_condition()  # Right associative
            return ConditionNode(
                type=ConditionType.UNARY,
                operand=operand
            )

        return self._parse_primary_condition()

    def _parse_primary_condition(self) -> ConditionNode:
        """Parse primary condition (parentheses or simple)"""
        # Parentheses
        if self._current_token().type == TokenType.LPAREN:
            self._consume(TokenType.LPAREN)
            condition = self._parse_or_condition()  # Recurse from top
            self._consume(TokenType.RPAREN)
            return condition

        # Simple condition
        return self._parse_simple_condition()

    def _parse_simple_condition(self) -> ConditionNode:
        """Parse simple condition: field operator value OR just field (for booleans)"""
        # Field
        if self._current_token().type != TokenType.IDENTIFIER:
            raise ValueError("Expected field name in WHERE clause")
        field = self._current_token().value
        self._advance()

        # Check if there's an operator or if it's a standalone boolean field
        op_token = self._current_token()

        # If no operator (boolean field like "visible" or "disabled")
        if op_token.type not in (
            TokenType.EQUALS, TokenType.NOT_EQUALS,
            TokenType.GT, TokenType.GTE, TokenType.LT, TokenType.LTE,
            TokenType.CONTAINS, TokenType.STARTS, TokenType.ENDS, TokenType.MATCHES
        ):
            # Treat as boolean field (field = true)
            return ConditionNode(
                type=ConditionType.SIMPLE,
                field=field,
                operator=Operator.EQUALS,
                value=True
            )

        # Operator
        operator = self._token_to_operator(op_token)
        self._advance()

        # Value
        value = self._parse_value()

        return ConditionNode(
            type=ConditionType.SIMPLE,
            field=field,
            operator=operator,
            value=value
        )

    def _token_to_operator(self, token: Token) -> Operator:
        """Convert token to Operator enum"""
        mapping = {
            TokenType.EQUALS: Operator.EQUALS,
            TokenType.NOT_EQUALS: Operator.NOT_EQUALS,
            TokenType.GT: Operator.GT,
            TokenType.GTE: Operator.GTE,
            TokenType.LT: Operator.LT,
            TokenType.LTE: Operator.LTE,
            TokenType.CONTAINS: Operator.CONTAINS,
            TokenType.STARTS: Operator.STARTS,
            TokenType.ENDS: Operator.ENDS,
            TokenType.MATCHES: Operator.MATCHES,
        }
        if token.type not in mapping:
            raise ValueError(f"Invalid operator: {token.type}")
        return mapping[token.type]

    def _parse_value(self) -> Any:
        """Parse value (string, number, boolean, identifier)"""
        token = self._current_token()

        if token.type == TokenType.STRING:
            value = token.value
            self._advance()
            return value
        elif token.type == TokenType.NUMBER:
            value = int(token.value)
            self._advance()
            return value
        elif token.type == TokenType.TRUE:
            self._advance()
            return True
        elif token.type == TokenType.FALSE:
            self._advance()
            return False
        elif token.type == TokenType.IDENTIFIER:
            # Field reference (like "visible" as boolean field)
            value = token.value
            self._advance()
            return value
        else:
            raise ValueError(f"Expected value, got {token.type}")

    # ========== Helper Methods ==========

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
