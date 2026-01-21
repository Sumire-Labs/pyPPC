"""
pyPPC - Parser
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from .lexer import Token, TokenType, tokenize
from .exceptions import ParseError


@dataclass
class ValueNode:
    """Represents a value in the AST."""
    value: Any
    type_hint: Optional[str] = None
    env_var: Optional[str] = None
    secret: Optional[str] = None
    default: Optional["ValueNode"] = None
    line: int = 0


@dataclass
class AssignmentNode:
    """Represents a key = value assignment."""
    key: str
    value: ValueNode
    line: int = 0


@dataclass
class SectionNode:
    """Represents a section >> name."""
    name: str
    assignments: List[AssignmentNode] = field(default_factory=list)
    line: int = 0


@dataclass
class ConditionalNode:
    """Represents a conditional >> @when condition."""
    condition: str
    sections: List[SectionNode] = field(default_factory=list)
    line: int = 0


@dataclass
class IncludeNode:
    """Represents @include directive."""
    path: str
    line: int = 0


@dataclass
class AST:
    """Abstract Syntax Tree for pyPPC."""
    sections: List[SectionNode] = field(default_factory=list)
    conditionals: List[ConditionalNode] = field(default_factory=list)
    includes: List[IncludeNode] = field(default_factory=list)


class Parser:
    """Parses tokens into AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.NEWLINE)]
        self.pos = 0
        self.current_section: Optional[SectionNode] = None
        self.current_conditional: Optional[ConditionalNode] = None

    def _current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Optional[Token]:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]

    def _advance(self) -> Optional[Token]:
        token = self._current()
        self.pos += 1
        return token

    def _skip_indent(self):
        while self._current() and self._current().type == TokenType.INDENT:
            self._advance()

    def _expect(self, token_type: TokenType) -> Token:
        token = self._current()
        if token is None or token.type != token_type:
            expected = token_type.name
            got = token.type.name if token else "EOF"
            line = token.line if token else 0
            raise ParseError(f"Expected {expected}, got {got}", line=line)
        return self._advance()

    def _parse_value(self) -> ValueNode:
        """Parse a value (possibly with default)."""
        self._skip_indent()
        token = self._current()

        if token is None:
            raise ParseError("Expected value, got EOF")

        node = ValueNode(value=None, line=token.line)

        # Array
        if token.type == TokenType.LBRACKET:
            node.value = self._parse_array()
            return node

        # Environment variable
        if token.type == TokenType.ENV_VAR:
            node.env_var = token.value
            node.value = None
            self._advance()

        # Secret
        elif token.type == TokenType.SECRET:
            node.secret = token.value
            node.value = None
            self._advance()

        # String
        elif token.type == TokenType.STRING:
            node.value = token.value
            self._advance()

        # Number
        elif token.type == TokenType.NUMBER:
            if "." in token.value:
                node.value = float(token.value)
            else:
                node.value = int(token.value)
            self._advance()

        # Boolean
        elif token.type == TokenType.BOOLEAN:
            node.value = token.value == "true"
            self._advance()

        # Null
        elif token.type == TokenType.NULL:
            node.value = None
            self._advance()

        else:
            raise ParseError(f"Unexpected token: {token.type.name}", line=token.line)

        # Check for default operator
        if self._current() and self._current().type == TokenType.DEFAULT_OP:
            self._advance()  # Skip ??
            node.default = self._parse_value()

        return node

    def _parse_array(self) -> List[Any]:
        """Parse an array value."""
        self._expect(TokenType.LBRACKET)
        items = []

        while self._current() and self._current().type != TokenType.RBRACKET:
            self._skip_indent()

            if self._current().type == TokenType.RBRACKET:
                break

            value_node = self._parse_value()

            # Extract raw value from node
            if value_node.env_var:
                items.append({"$env": value_node.env_var})
            elif value_node.secret:
                items.append({"$secret": value_node.secret})
            else:
                items.append(value_node.value)

            self._skip_indent()

            if self._current() and self._current().type == TokenType.COMMA:
                self._advance()

        self._expect(TokenType.RBRACKET)
        return items

    def _parse_assignment(self) -> AssignmentNode:
        """Parse a key = value assignment."""
        self._skip_indent()
        key_token = self._expect(TokenType.KEY)

        type_hint = None
        if self._current() and self._current().type == TokenType.TYPE_HINT:
            type_hint = self._current().value
            self._advance()

        self._expect(TokenType.EQUALS)

        value_node = self._parse_value()
        value_node.type_hint = type_hint

        return AssignmentNode(
            key=key_token.value,
            value=value_node,
            line=key_token.line
        )

    def parse(self) -> AST:
        """Parse tokens into AST."""
        ast = AST()

        while self._current() and self._current().type != TokenType.EOF:
            self._skip_indent()
            token = self._current()

            if token is None or token.type == TokenType.EOF:
                break

            # Section
            if token.type == TokenType.SECTION:
                self.current_conditional = None
                section = SectionNode(name=token.value, line=token.line)
                self.current_section = section
                ast.sections.append(section)
                self._advance()

            # Conditional section
            elif token.type == TokenType.SECTION_WHEN:
                conditional = ConditionalNode(condition=token.value, line=token.line)
                self.current_conditional = conditional
                self.current_section = None
                ast.conditionals.append(conditional)
                self._advance()

                # Parse sections within conditional
                self._skip_indent()
                while self._current() and self._current().type == TokenType.SECTION:
                    section = SectionNode(name=self._current().value, line=self._current().line)
                    self.current_section = section
                    conditional.sections.append(section)
                    self._advance()

                    # Parse assignments in this section
                    self._skip_indent()
                    while self._current() and self._current().type == TokenType.KEY:
                        assignment = self._parse_assignment()
                        section.assignments.append(assignment)
                        self._skip_indent()

            # Include
            elif token.type == TokenType.INCLUDE:
                include = IncludeNode(path=token.value, line=token.line)
                ast.includes.append(include)
                self._advance()

            # Assignment (within current section)
            elif token.type == TokenType.KEY:
                assignment = self._parse_assignment()
                if self.current_section:
                    self.current_section.assignments.append(assignment)
                else:
                    # Global assignment - create implicit root section
                    if not ast.sections or ast.sections[0].name != "":
                        root_section = SectionNode(name="", line=token.line)
                        ast.sections.insert(0, root_section)
                    ast.sections[0].assignments.append(assignment)

            else:
                self._advance()

        return ast


def parse(text: str) -> AST:
    """Convenience function to parse text into AST."""
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()
