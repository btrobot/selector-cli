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

    # Element types
    INPUT = auto()
    BUTTON = auto()
    SELECT = auto()
    TEXTAREA = auto()
    LINK = auto()
    ALL = auto()

    # Operators
    EQUALS = auto()
    NOT_EQUALS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Literals
    STRING = auto()
    NUMBER = auto()

    # Delimiters
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()

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
        'input': TokenType.INPUT,
        'button': TokenType.BUTTON,
        'select': TokenType.SELECT,
        'textarea': TokenType.TEXTAREA,
        'a': TokenType.LINK,
        'all': TokenType.ALL,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
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
            if self._current_char() == '=':
                tokens.append(Token(TokenType.EQUALS, '=', self.position))
                self.position += 1
                continue

            if self._current_char() == '!' and self._peek() == '=':
                tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.position))
                self.position += 2
                continue

            if self._current_char() == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', self.position))
                self.position += 1
                continue

            if self._current_char() == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', self.position))
                self.position += 1
                continue

            if self._current_char() == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.position))
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
