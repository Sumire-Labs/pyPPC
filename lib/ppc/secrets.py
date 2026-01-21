"""
pyPPC - Secrets Management
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Optional, Callable
from .exceptions import SecretError


class SecretProvider:
    """Base class for secret providers."""

    def get(self, key: str) -> Optional[str]:
        """Get a secret value by key."""
        raise NotImplementedError


class EnvSecretProvider(SecretProvider):
    """
    Provides secrets from environment variables.
    Looks for SECRET_<key> or PEPECONFIG_SECRET_<key>.
    """

    def __init__(self, prefix: str = "SECRET_"):
        self.prefix = prefix

    def get(self, key: str) -> Optional[str]:
        # Try with prefix
        value = os.environ.get(f"{self.prefix}{key}")
        if value:
            return value

        # Try PEPECONFIG prefix
        value = os.environ.get(f"PEPECONFIG_SECRET_{key}")
        if value:
            return value

        return None


class FileSecretProvider(SecretProvider):
    """
    Provides secrets from a JSON file.
    File format: {"secret_name": "secret_value", ...}
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self._secrets: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            raise SecretError(f"Secrets file not found: {self.path}")

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self._secrets = json.load(f)
        except json.JSONDecodeError as e:
            raise SecretError(f"Invalid JSON in secrets file: {e}")
        except Exception as e:
            raise SecretError(f"Error reading secrets file: {e}")

    def get(self, key: str) -> Optional[str]:
        return self._secrets.get(key)


class DictSecretProvider(SecretProvider):
    """
    Simple in-memory secret provider.
    Useful for testing or programmatic secret injection.
    """

    def __init__(self, secrets: Dict[str, str] = None):
        self._secrets = secrets or {}

    def get(self, key: str) -> Optional[str]:
        return self._secrets.get(key)

    def set(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def delete(self, key: str) -> None:
        self._secrets.pop(key, None)


class ChainedSecretProvider(SecretProvider):
    """
    Chains multiple secret providers.
    Returns the first non-None value found.
    """

    def __init__(self, *providers: SecretProvider):
        self.providers = list(providers)

    def get(self, key: str) -> Optional[str]:
        for provider in self.providers:
            value = provider.get(key)
            if value is not None:
                return value
        return None

    def add_provider(self, provider: SecretProvider) -> None:
        self.providers.append(provider)


def create_secret_provider(
    env: bool = True,
    file_path: Optional[Path] = None,
    secrets: Optional[Dict[str, str]] = None,
) -> SecretProvider:
    """
    Factory function to create a secret provider.

    Args:
        env: Whether to include environment variable provider
        file_path: Optional path to a secrets JSON file
        secrets: Optional dictionary of secrets

    Returns:
        A SecretProvider instance (possibly chained)
    """
    providers = []

    if secrets:
        providers.append(DictSecretProvider(secrets))

    if file_path:
        providers.append(FileSecretProvider(file_path))

    if env:
        providers.append(EnvSecretProvider())

    if len(providers) == 0:
        return EnvSecretProvider()
    elif len(providers) == 1:
        return providers[0]
    else:
        return ChainedSecretProvider(*providers)
