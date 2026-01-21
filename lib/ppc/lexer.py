"""
pyPPC - Lexer (Tokenizer)
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator
from .exceptions import LexerError


class TokenType(Enum):
    """Token types for pyPPC."""
    # Structure
    SECTION = auto()          # >> section_name
    SECTION_WHEN = auto()     # >> @when condition
    INCLUDE = auto()          # @include "file"

    # Assignment
    KEY = auto()              # key
    TYPE_HINT = auto()        # :: type
    EQUALS = auto()           # =
    VALUE = auto()            # value

    # Values
    STRING = auto()           # "string" or 'string'
    NUMBER = auto()           # 123 or 1.5
    BOOLEAN = auto()          # true/false
    NULL = auto()             # null/none
    ENV_VAR = auto()          # $env.NAME
    SECRET = auto()           # $secret.NAME
    DEFAULT_OP = auto()       # ??

    # Collections
    LBRACKET = auto()         # [
    RBRACKET = auto()         # ]
    COMMA = auto()            # ,

    # Other
    COMMENT = auto()          # # comment
    NEWLINE = auto()
    INDENT = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.column})"


class Lexer:
    """Tokenizes pyPPC text."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def _peek(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.text):
            return None
        return self.text[pos]

    def _advance(self, count: int = 1) -> str:
        result = ""
        for _ in range(count):
            if self.pos < len(self.text):
                char = self.text[self.pos]
                result += char
                self.pos += 1
                if char == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
        return result

    def _skip_whitespace_on_line(self) -> int:
        """Skip spaces/tabs, return count. Stops at newline."""
        count = 0
        while self._current_char() in (" ", "\t"):
            self._advance()
            count += 1
        return count

    def _read_until(self, end_chars: str, include_end: bool = False) -> str:
        result = ""
        while self._current_char() is not None and self._current_char() not in end_chars:
            result += self._advance()
        if include_end and self._current_char() in end_chars:
            result += self._advance()
        return result

    def _read_string(self, quote_char: str) -> str:
        """Read a quoted string."""
        self._advance()  # Skip opening quote
        result = ""
        while self._current_char() is not None:
            char = self._current_char()
            if char == "\\":
                self._advance()
                next_char = self._current_char()
                if next_char == "n":
                    result += "\n"
                elif next_char == "t":
                    result += "\t"
                elif next_char == "\\":
                    result += "\\"
                elif next_char == quote_char:
                    result += quote_char
                else:
                    result += next_char or ""
                self._advance()
            elif char == quote_char:
                self._advance()  # Skip closing quote
                break
            else:
                result += self._advance()
        return result

    def _read_array(self) -> List[Token]:
        """Read array tokens."""
        tokens = []
        start_line = self.line
        start_col = self.column
        self._advance()  # Skip [
        tokens.append(Token(TokenType.LBRACKET, "[", start_line, start_col))

        while self._current_char() is not None and self._current_char() != "]":
            self._skip_whitespace_on_line()

            # Skip newlines inside arrays
            while self._current_char() == "\n":
                self._advance()
                self._skip_whitespace_on_line()

            if self._current_char() == "]":
                break

            # Skip comments inside arrays
            if self._current_char() == "#":
                self._read_until("\n")
                continue

            # Read value
            val_tokens = self._read_value_token()
            tokens.extend(val_tokens)

            self._skip_whitespace_on_line()

            # Comma
            if self._current_char() == ",":
                tokens.append(Token(TokenType.COMMA, ",", self.line, self.column))
                self._advance()

        if self._current_char() == "]":
            tokens.append(Token(TokenType.RBRACKET, "]", self.line, self.column))
            self._advance()

        return tokens

    def _read_value_token(self) -> List[Token]:
        """Read a single value and return tokens."""
        tokens = []
        start_line = self.line
        start_col = self.column

        char = self._current_char()

        # String
        if char in ('"', "'"):
            value = self._read_string(char)
            tokens.append(Token(TokenType.STRING, value, start_line, start_col))

        # Array
        elif char == "[":
            tokens.extend(self._read_array())

        # Environment variable
        elif char == "$":
            self._advance()  # Skip $
            if self._current_char() == "e" and self.text[self.pos:self.pos+3] == "env":
                self._advance(4)  # Skip 'env.'
                name = ""
                while self._current_char() and (self._current_char().isalnum() or self._current_char() == "_"):
                    name += self._advance()
                tokens.append(Token(TokenType.ENV_VAR, name, start_line, start_col))
            elif self._current_char() == "s" and self.text[self.pos:self.pos+6] == "secret":
                self._advance(7)  # Skip 'secret.'
                name = ""
                while self._current_char() and (self._current_char().isalnum() or self._current_char() == "_"):
                    name += self._advance()
                tokens.append(Token(TokenType.SECRET, name, start_line, start_col))
            else:
                raise LexerError(f"Invalid variable reference", line=start_line, column=start_col)

        # Number or unquoted value
        else:
            value = ""
            while self._current_char() and self._current_char() not in (" ", "\t", "\n", "#", ",", "]", "?"):
                value += self._advance()

            if not value:
                return tokens

            # Check for boolean
            if value.lower() in ("true", "yes", "on"):
                tokens.append(Token(TokenType.BOOLEAN, "true", start_line, start_col))
            elif value.lower() in ("false", "no", "off"):
                tokens.append(Token(TokenType.BOOLEAN, "false", start_line, start_col))
            elif value.lower() in ("null", "none", "nil"):
                tokens.append(Token(TokenType.NULL, "null", start_line, start_col))
            else:
                # Try number
                try:
                    if "." in value:
                        float(value)
                    else:
                        int(value)
                    tokens.append(Token(TokenType.NUMBER, value, start_line, start_col))
                except ValueError:
                    tokens.append(Token(TokenType.STRING, value, start_line, start_col))

        # Check for default operator
        self._skip_whitespace_on_line()
        if self._current_char() == "?" and self._peek() == "?":
            tokens.append(Token(TokenType.DEFAULT_OP, "??", self.line, self.column))
            self._advance(2)
            self._skip_whitespace_on_line()
            tokens.extend(self._read_value_token())

        return tokens

    def tokenize(self) -> List[Token]:
        """Tokenize the entire text."""
        self.tokens = []

        while self._current_char() is not None:
            char = self._current_char()
            start_line = self.line
            start_col = self.column

            # Newline
            if char == "\n":
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", start_line, start_col))
                self._advance()
                # Check for indentation
                indent = self._skip_whitespace_on_line()
                if indent > 0 and self._current_char() not in (None, "\n", "#"):
                    self.tokens.append(Token(TokenType.INDENT, " " * indent, self.line, 1))
                continue

            # Whitespace (not at start of line)
            if char in (" ", "\t"):
                self._skip_whitespace_on_line()
                continue

            # Comment
            if char == "#":
                comment = self._read_until("\n").strip()
                self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_col))
                continue

            # Section >> or >> @when
            if char == ">" and self._peek() == ">":
                self._advance(2)  # Skip >>
                self._skip_whitespace_on_line()

                # Check for @when
                if self._current_char() == "@" and self.text[self.pos:self.pos+5] == "@when":
                    self._advance(5)  # Skip @when
                    self._skip_whitespace_on_line()
                    condition = self._read_until("\n").strip()
                    self.tokens.append(Token(TokenType.SECTION_WHEN, condition, start_line, start_col))
                else:
                    name = self._read_until("\n#").strip()
                    self.tokens.append(Token(TokenType.SECTION, name, start_line, start_col))
                continue

            # Include @include
            if char == "@" and self.text[self.pos:self.pos+8] == "@include":
                self._advance(8)  # Skip @include
                self._skip_whitespace_on_line()
                # Read the file path
                if self._current_char() in ('"', "'"):
                    path = self._read_string(self._current_char())
                else:
                    path = self._read_until("\n#").strip()
                self.tokens.append(Token(TokenType.INCLUDE, path, start_line, start_col))
                continue

            # Key = value or key :: type = value
            if char.isalnum() or char == "_":
                key = ""
                while self._current_char() and (self._current_char().isalnum() or self._current_char() in ("_", "-")):
                    key += self._advance()

                self.tokens.append(Token(TokenType.KEY, key, start_line, start_col))
                self._skip_whitespace_on_line()

                # Type hint ::
                if self._current_char() == ":" and self._peek() == ":":
                    self._advance(2)
                    self._skip_whitespace_on_line()
                    type_name = ""
                    while self._current_char() and self._current_char().isalnum():
                        type_name += self._advance()
                    self.tokens.append(Token(TokenType.TYPE_HINT, type_name, self.line, self.column))
                    self._skip_whitespace_on_line()

                # Equals
                if self._current_char() == "=":
                    self.tokens.append(Token(TokenType.EQUALS, "=", self.line, self.column))
                    self._advance()
                    self._skip_whitespace_on_line()

                    # Value
                    value_tokens = self._read_value_token()
                    self.tokens.extend(value_tokens)
                continue

            # Unknown character
            raise LexerError(f"Unexpected character: {char}", line=start_line, column=start_col)

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


def tokenize(text: str) -> List[Token]:
    """Convenience function to tokenize text."""
    lexer = Lexer(text)
    return lexer.tokenize()
