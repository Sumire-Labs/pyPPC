"""
pyPPC - Custom Exceptions
"""


class PPCError(Exception):
    """Base exception for all pyPPC errors."""

    def __init__(self, message: str, line: int = None, column: int = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.line is not None:
            location = f" (line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
            location += ")"
            return f"{self.message}{location}"
        return self.message


class LexerError(PPCError):
    """Error during tokenization."""
    pass


class ParseError(PPCError):
    """Error during parsing."""
    pass


class TypeError(PPCError):
    """Type validation error."""
    pass


class EvaluationError(PPCError):
    """Error during evaluation (env vars, secrets, etc.)."""
    pass


class IncludeError(PPCError):
    """Error when including another file."""
    pass


class SecretError(PPCError):
    """Error related to secrets management."""
    pass


class FileNotFoundError(PPCError):
    """Config file not found."""
    pass
