"""
pyPPC - Config Object
"""

from typing import Any, Dict, Iterator, Optional, Union


class ConfigSection:
    """
    Represents a section of the config.
    Supports both dot notation (config.key) and dict notation (config["key"]).
    """

    def __init__(self, data: Dict[str, Any] = None, name: str = ""):
        object.__setattr__(self, "_data", data or {})
        object.__setattr__(self, "_name", name)

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_"):
            return object.__getattribute__(self, key)

        data = object.__getattribute__(self, "_data")
        if key not in data:
            raise AttributeError(f"Config has no attribute '{key}'")

        value = data[key]
        if isinstance(value, dict):
            return ConfigSection(value, key)
        return value

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        value = self._data[key]
        if isinstance(value, dict):
            return ConfigSection(value, key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"ConfigSection({self._data})"

    def __str__(self) -> str:
        return str(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with an optional default."""
        try:
            value = self._data.get(key, default)
            if isinstance(value, dict):
                return ConfigSection(value, key)
            return value
        except KeyError:
            return default

    def keys(self):
        """Return config keys."""
        return self._data.keys()

    def values(self):
        """Return config values."""
        return self._data.values()

    def items(self):
        """Return config items."""
        return self._data.items()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to regular dictionary."""
        return dict(self._data)


class Config(ConfigSection):
    """
    Root config object.
    Supports nested access via dot notation: config.section.key
    """

    def __init__(self, data: Dict[str, Any] = None):
        super().__init__(data, "root")

    def __repr__(self) -> str:
        return f"Config({self._data})"

    def merge(self, other: Union["Config", Dict[str, Any]]) -> "Config":
        """Merge another config into this one."""
        if isinstance(other, Config):
            other_data = other._data
        else:
            other_data = other

        self._deep_merge(self._data, other_data)
        return self

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def set_nested(self, path: str, value: Any) -> None:
        """
        Set a nested value using dot notation path.
        Example: config.set_nested("database.host", "localhost")
        """
        parts = path.split(".")
        current = self._data

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    def get_nested(self, path: str, default: Any = None) -> Any:
        """
        Get a nested value using dot notation path.
        Example: config.get_nested("database.host")
        """
        parts = path.split(".")
        current = self._data

        try:
            for part in parts:
                current = current[part]
            if isinstance(current, dict):
                return ConfigSection(current, parts[-1])
            return current
        except (KeyError, TypeError):
            return default
