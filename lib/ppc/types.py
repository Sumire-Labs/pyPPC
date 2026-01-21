"""
pyPPC - Type System
"""

from typing import Any, List, Union
from enum import Enum
from .exceptions import TypeError


class PPCType(Enum):
    """Supported types in pyPPC."""
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    ANY = "any"

    @classmethod
    def from_string(cls, type_str: str) -> "PPCType":
        """Convert string to PPCType."""
        type_map = {
            "str": cls.STR,
            "string": cls.STR,
            "int": cls.INT,
            "integer": cls.INT,
            "float": cls.FLOAT,
            "number": cls.FLOAT,
            "bool": cls.BOOL,
            "boolean": cls.BOOL,
            "list": cls.LIST,
            "array": cls.LIST,
            "any": cls.ANY,
        }
        normalized = type_str.lower().strip()
        if normalized not in type_map:
            raise TypeError(f"Unknown type: {type_str}")
        return type_map[normalized]


def validate_type(value: Any, expected_type: PPCType, line: int = None) -> Any:
    """Validate and convert value to expected type."""

    if expected_type == PPCType.ANY:
        return value

    if expected_type == PPCType.STR:
        return str(value)

    if expected_type == PPCType.INT:
        try:
            if isinstance(value, bool):
                raise ValueError()
            return int(value)
        except (ValueError, TypeError):
            raise TypeError(f"Cannot convert '{value}' to int", line=line)

    if expected_type == PPCType.FLOAT:
        try:
            if isinstance(value, bool):
                raise ValueError()
            return float(value)
        except (ValueError, TypeError):
            raise TypeError(f"Cannot convert '{value}' to float", line=line)

    if expected_type == PPCType.BOOL:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower = value.lower()
            if lower in ("true", "yes", "on", "1"):
                return True
            if lower in ("false", "no", "off", "0"):
                return False
        raise TypeError(f"Cannot convert '{value}' to bool", line=line)

    if expected_type == PPCType.LIST:
        if isinstance(value, list):
            return value
        raise TypeError(f"Expected list, got {type(value).__name__}", line=line)

    return value


def infer_type(value: Any) -> PPCType:
    """Infer PPCType from Python value."""
    if isinstance(value, bool):
        return PPCType.BOOL
    if isinstance(value, int):
        return PPCType.INT
    if isinstance(value, float):
        return PPCType.FLOAT
    if isinstance(value, str):
        return PPCType.STR
    if isinstance(value, list):
        return PPCType.LIST
    return PPCType.ANY


def parse_value(raw_value: str) -> Any:
    """Parse a raw string value into appropriate Python type."""
    stripped = raw_value.strip()

    # Empty string
    if not stripped:
        return ""

    # Boolean
    if stripped.lower() in ("true", "yes", "on"):
        return True
    if stripped.lower() in ("false", "no", "off"):
        return False

    # None/null
    if stripped.lower() in ("null", "none", "nil"):
        return None

    # Quoted string
    if (stripped.startswith('"') and stripped.endswith('"')) or \
       (stripped.startswith("'") and stripped.endswith("'")):
        return stripped[1:-1]

    # Integer
    try:
        return int(stripped)
    except ValueError:
        pass

    # Float
    try:
        return float(stripped)
    except ValueError:
        pass

    # Default to string
    return stripped
