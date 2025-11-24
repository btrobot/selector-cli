"""
Lexer for Selector CLI
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import List


class TokenType(Enum):
    """Token types"""
    # Keywords
    OPEN = auto()
    SCAN = auto()
    ADD = auto()
    REMOVE = auto()
    CLEAR = auto()
    LIST = auto()
    SHOW = auto()
    COUNT = auto()
    WHERE = auto()
    QUIT = auto()
    EXIT = auto()
    HELP = auto()
    EXPORT = auto()  # Phase 3

    # V2 - Extended commands
    FIND = auto()
    PREVIEW = auto()
    APPEND = auto()

    # Phase 4 - Persistence
    SAVE = auto()
    LOAD = auto()
    SAVED = auto()
    DELETE = auto()
    SET = auto()
    VARS = auto()
    MACRO = auto()
    RUN = auto()
    MACROS = auto()
    EXEC = auto()

    # Phase 5 - Advanced Features
    HIGHLIGHT = auto()
    UNHIGHLIGHT = auto()
    UNION = auto()
    INTERSECT = auto()
    DIFFERENCE = auto()
    UNIQUE = auto()
    HISTORY = auto()
    BANG = auto()  # ! for history (!n, !!)

    # Phase 2 - Filtering
    KEEP = auto()
    FILTER = auto()

    # Element types
    INPUT = auto()
    BUTTON = auto()
    SELECT = auto()
    TEXTAREA = auto()
    LINK = auto()
    ALL = auto()
    DIV = auto()

    # Export formats (Phase 3)
    PLAYWRIGHT = auto()
    SELENIUM = auto()
    PUPPETEER = auto()
    JSON = auto()
    CSV = auto()
    YAML = auto()

    # Operators
    EQUALS = auto()
    NOT_EQUALS = auto()
    GT = auto()         # > (also used for file redirection)
    GTE = auto()        # >=
    LT = auto()         # <
    LTE = auto()        # <=
    AND = auto()
    OR = auto()
    NOT = auto()

    # String operators
    CONTAINS = auto()
    STARTS = auto()
    ENDS = auto()
    MATCHES = auto()

    # Literals
    STRING = auto()
    NUMBER = auto()
    TRUE = auto()
    FALSE = auto()

    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COMMA = auto()      # ,
    DASH = auto()       # -

    # V2 - Additional tokens
    DOT = auto()        # . (for .find)
    DOUBLE_DASH = auto()  # -- (for options like --deep)
    FROM = auto()       # from

    # Other
    IDENTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    """Token representation"""
    type: TokenType
    value: str
    position: int


class Lexer:
    """Tokenize command strings"""

    KEYWORDS = {
        # Commands
        'open': TokenType.OPEN,
        'scan': TokenType.SCAN,
        'add': TokenType.ADD,
        'remove': TokenType.REMOVE,
        'clear': TokenType.CLEAR,
        'list': TokenType.LIST,
        'ls': TokenType.LIST,
        'show': TokenType.SHOW,
        'count': TokenType.COUNT,
        'where': TokenType.WHERE,
        'quit': TokenType.QUIT,
        'exit': TokenType.EXIT,
        'q': TokenType.QUIT,
        'help': TokenType.HELP,
        'export': TokenType.EXPORT,  # Phase 3

        # V2 - Extended commands
        'find': TokenType.FIND,
        'preview': TokenType.PREVIEW,
        'append': TokenType.APPEND,

        # Phase 4 - Persistence
        'save': TokenType.SAVE,
        'load': TokenType.LOAD,
        'saved': TokenType.SAVED,
        'delete': TokenType.DELETE,
        'set': TokenType.SET,
        'vars': TokenType.VARS,
        'macro': TokenType.MACRO,
        'run': TokenType.RUN,
        'macros': TokenType.MACROS,
        'exec': TokenType.EXEC,

        # Phase 5 - Advanced Features
        'highlight': TokenType.HIGHLIGHT,
        'unhighlight': TokenType.UNHIGHLIGHT,
        'union': TokenType.UNION,
        'intersect': TokenType.INTERSECT,
        'difference': TokenType.DIFFERENCE,
        'unique': TokenType.UNIQUE,
        'history': TokenType.HISTORY,

        # Phase 2 - Filtering
        'keep': TokenType.KEEP,
        'filter': TokenType.FILTER,

        # Element types
        'input': TokenType.INPUT,
        'button': TokenType.BUTTON,
        'select': TokenType.SELECT,
        'textarea': TokenType.TEXTAREA,
        'a': TokenType.LINK,
        'link': TokenType.LINK,
        'all': TokenType.ALL,
        'div': TokenType.DIV,

        # Export formats (Phase 3)
        'playwright': TokenType.PLAYWRIGHT,
        'selenium': TokenType.SELENIUM,
        'puppeteer': TokenType.PUPPETEER,
        'json': TokenType.JSON,
        'csv': TokenType.CSV,
        'yaml': TokenType.YAML,

        # V2 keywords
        'from': TokenType.FROM,

        # Logical operators
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,

        # String operators
        'contains': TokenType.CONTAINS,
        'starts': TokenType.STARTS,
        'ends': TokenType.ENDS,
        'matches': TokenType.MATCHES,

        # Boolean literals
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
    }

    def __init__(self):
        self.text = ""
        self.position = 0

    def tokenize(self, text: str) -> List[Token]:
        """Convert string to tokens"""
        self.text = text.strip()
        self.position = 0
        tokens = []

        while self.position < len(self.text):
            # Skip whitespace
            if self._current_char().isspace():
                self.position += 1
                continue

            # String
            if self._current_char() in '"\'':
                tokens.append(self._read_string())
                continue

            # Number
            if self._current_char().isdigit():
                tokens.append(self._read_number())
                continue

            # Identifier or keyword
            if self._current_char().isalpha() or self._current_char() == '_':
                tokens.append(self._read_identifier())
                continue

            # Operators and delimiters
            # Greater than or equal
            if self._current_char() == '>' and self._peek() == '=':
                tokens.append(Token(TokenType.GTE, '>=', self.position))
                self.position += 2
                continue

            # Greater than
            if self._current_char() == '>':
                tokens.append(Token(TokenType.GT, '>', self.position))
                self.position += 1
                continue

            # Less than or equal
            if self._current_char() == '<' and self._peek() == '=':
                tokens.append(Token(TokenType.LTE, '<=', self.position))
                self.position += 2
                continue

            # Less than
            if self._current_char() == '<':
                tokens.append(Token(TokenType.LT, '<', self.position))
                self.position += 1
                continue

            # Equals
            if self._current_char() == '=':
                tokens.append(Token(TokenType.EQUALS, '=', self.position))
                self.position += 1
                continue

            # Not equals
            if self._current_char() == '!' and self._peek() == '=':
                tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.position))
                self.position += 2
                continue

            # Bang (history commands: !n or !!)
            if self._current_char() == '!':
                tokens.append(Token(TokenType.BANG, '!', self.position))
                self.position += 1
                continue

            # Left parenthesis
            if self._current_char() == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.position))
                self.position += 1
                continue

            # Right parenthesis
            if self._current_char() == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.position))
                self.position += 1
                continue

            # Left bracket
            if self._current_char() == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', self.position))
                self.position += 1
                continue

            # Right bracket
            if self._current_char() == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', self.position))
                self.position += 1
                continue

            # Left brace
            if self._current_char() == '{':
                tokens.append(Token(TokenType.LBRACE, '{', self.position))
                self.position += 1
                continue

            # Right brace
            if self._current_char() == '}':
                tokens.append(Token(TokenType.RBRACE, '}', self.position))
                self.position += 1
                continue

            # Comma
            if self._current_char() == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.position))
                self.position += 1
                continue

            # Asterisk (for wildcard like find *)
            if self._current_char() == '*':
                tokens.append(Token(TokenType.ALL, '*', self.position))
                self.position += 1
                continue

            # Dash (for ranges like [1-10])
            if self._current_char() == '-':
                # Check for double dash (--)
                if self._peek() == '-':
                    tokens.append(Token(TokenType.DOUBLE_DASH, '--', self.position))
                    self.position += 2
                else:
                    tokens.append(Token(TokenType.DASH, '-', self.position))
                    self.position += 1
                continue

            # Dot (for .find)
            if self._current_char() == '.':
                tokens.append(Token(TokenType.DOT, '.', self.position))
                self.position += 1
                continue

            # Unknown character
            raise ValueError(f"Unexpected character: {self._current_char()} at position {self.position}")

        tokens.append(Token(TokenType.EOF, '', self.position))
        return tokens

    def _current_char(self) -> str:
        """Get current character"""
        if self.position >= len(self.text):
            return ''
        return self.text[self.position]

    def _peek(self, offset: int = 1) -> str:
        """Peek ahead"""
        pos = self.position + offset
        if pos >= len(self.text):
            return ''
        return self.text[pos]

    def _read_string(self) -> Token:
        """Read string literal"""
        start_pos = self.position
        quote = self._current_char()
        self.position += 1  # Skip opening quote

        value = ''
        while self.position < len(self.text) and self._current_char() != quote:
            value += self._current_char()
            self.position += 1

        if self._current_char() == quote:
            self.position += 1  # Skip closing quote

        return Token(TokenType.STRING, value, start_pos)

    def _read_number(self) -> Token:
        """Read number"""
        start_pos = self.position
        value = ''

        while self.position < len(self.text) and self._current_char().isdigit():
            value += self._current_char()
            self.position += 1

        return Token(TokenType.NUMBER, value, start_pos)

    def _read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_pos = self.position
        value = ''

        while self.position < len(self.text) and (
            self._current_char().isalnum() or self._current_char() in '_-.:/'
        ):
            value += self._current_char()
            self.position += 1

        # Check if it's a keyword
        token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)

        return Token(token_type, value, start_pos)
