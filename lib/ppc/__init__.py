"""
pyPPC - A human-readable configuration format for Python

Usage:
    from ppc import load, loads

    # Load from file
    config = load("config.ppc")
    print(config.bot.token)

    # Load from string
    config = loads('''
    >> bot
      token = "abc123"
    ''')
"""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"  # Fallback for development

__author__ = "pyPPC"

from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable

from .config import Config, ConfigSection
from .parser import parse, AST
from .evaluator import Evaluator
from .lexer import tokenize
from .secrets import (
    SecretProvider,
    EnvSecretProvider,
    FileSecretProvider,
    DictSecretProvider,
    ChainedSecretProvider,
    create_secret_provider,
)
from .exceptions import (
    PPCError,
    LexerError,
    ParseError,
    TypeError,
    EvaluationError,
    IncludeError,
    SecretError,
)


def load(
    path: Union[str, Path],
    *,
    secret_provider: Optional[Callable[[str], Optional[str]]] = None,
    secrets_file: Optional[Union[str, Path]] = None,
    secrets: Optional[Dict[str, str]] = None,
) -> Config:
    """
    Load a pepeconfig file.

    Args:
        path: Path to the .ppc file
        secret_provider: Custom function to provide secrets
        secrets_file: Path to a JSON file containing secrets
        secrets: Dictionary of secrets

    Returns:
        Config object with parsed configuration

    Example:
        config = load("bot.ppc")
        print(config.bot.token)
    """
    path = Path(path)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Create secret provider if needed
    provider = None
    if secret_provider:
        provider = secret_provider
    elif secrets_file or secrets:
        sp = create_secret_provider(
            env=True,
            file_path=Path(secrets_file) if secrets_file else None,
            secrets=secrets,
        )
        provider = sp.get

    ast = parse(text)
    evaluator = Evaluator(base_path=path.parent, secret_provider=provider)
    return evaluator.evaluate(ast)


def loads(
    text: str,
    *,
    base_path: Optional[Union[str, Path]] = None,
    secret_provider: Optional[Callable[[str], Optional[str]]] = None,
    secrets: Optional[Dict[str, str]] = None,
) -> Config:
    """
    Load pepeconfig from a string.

    Args:
        text: The pepeconfig text
        base_path: Base path for resolving @include directives
        secret_provider: Custom function to provide secrets
        secrets: Dictionary of secrets

    Returns:
        Config object with parsed configuration

    Example:
        config = loads('''
        >> bot
          prefix = "!"
        ''')
    """
    provider = None
    if secret_provider:
        provider = secret_provider
    elif secrets:
        sp = DictSecretProvider(secrets)
        provider = sp.get

    ast = parse(text)
    evaluator = Evaluator(
        base_path=Path(base_path) if base_path else None,
        secret_provider=provider,
    )
    return evaluator.evaluate(ast)


def dump(config: Union[Config, Dict[str, Any]], path: Union[str, Path]) -> None:
    """
    Dump a Config object to a .ppc file.

    Args:
        config: Config object or dictionary to dump
        path: Path to write the .ppc file
    """
    text = dumps(config)
    path = Path(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def dumps(config: Union[Config, Dict[str, Any]]) -> str:
    """
    Dump a Config object to a string.

    Args:
        config: Config object or dictionary to dump

    Returns:
        The pepeconfig formatted string
    """
    if isinstance(config, Config):
        data = config.to_dict()
    else:
        data = config

    lines = []
    _dump_section(data, lines, "")
    return "\n".join(lines)


def _dump_section(
    data: Dict[str, Any],
    lines: list,
    prefix: str,
) -> None:
    """Recursively dump sections."""
    simple_items = {}
    nested_items = {}

    for key, value in data.items():
        if isinstance(value, dict):
            nested_items[key] = value
        else:
            simple_items[key] = value

    # Dump simple items first
    if simple_items:
        if prefix:
            lines.append(f">> {prefix}")
        for key, value in simple_items.items():
            formatted = _format_value(value)
            lines.append(f"  {key} = {formatted}")
        lines.append("")

    # Dump nested sections
    for key, value in nested_items.items():
        new_prefix = f"{prefix}.{key}" if prefix else key
        _dump_section(value, lines, new_prefix)


def _format_value(value: Any) -> str:
    """Format a value for output."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        # Escape and quote string
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        items = [_format_value(item) for item in value]
        return "[" + ", ".join(items) + "]"
    return str(value)


# Export public API
__all__ = [
    # Main functions
    "load",
    "loads",
    "dump",
    "dumps",
    # Classes
    "Config",
    "ConfigSection",
    # Secret providers
    "SecretProvider",
    "EnvSecretProvider",
    "FileSecretProvider",
    "DictSecretProvider",
    "ChainedSecretProvider",
    "create_secret_provider",
    # Exceptions
    "PPCError",
    "LexerError",
    "ParseError",
    "TypeError",
    "EvaluationError",
    "IncludeError",
    "SecretError",
    # Version
    "__version__",
]
