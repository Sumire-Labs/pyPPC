"""
pyPPC CLI - Internationalization (i18n)
"""

import locale
import os
from typing import Dict, Optional

from .ja import MESSAGES as JA_MESSAGES
from .en import MESSAGES as EN_MESSAGES

# Available languages
LANGUAGES = {
    "ja": JA_MESSAGES,
    "en": EN_MESSAGES,
}

# Current language
_current_lang = "en"


def detect_language() -> str:
    """Detect system language."""
    # Check environment variable first
    env_lang = os.environ.get("PPC_LANG", "").lower()
    if env_lang in LANGUAGES:
        return env_lang

    # Check system locale
    try:
        system_lang = locale.getdefaultlocale()[0]
        if system_lang:
            lang_code = system_lang.split("_")[0].lower()
            if lang_code in LANGUAGES:
                return lang_code
    except Exception:
        pass

    return "en"


def set_language(lang: str) -> None:
    """Set current language."""
    global _current_lang
    if lang in LANGUAGES:
        _current_lang = lang
    else:
        _current_lang = "en"


def get_language() -> str:
    """Get current language."""
    return _current_lang


def t(key: str, **kwargs) -> str:
    """
    Get translated message.

    Args:
        key: Message key (e.g., "validate.success")
        **kwargs: Format arguments

    Returns:
        Translated message
    """
    messages = LANGUAGES.get(_current_lang, EN_MESSAGES)

    # Navigate nested keys
    parts = key.split(".")
    value = messages
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            # Fallback to English
            value = EN_MESSAGES
            for p in parts:
                if isinstance(value, dict) and p in value:
                    value = value[p]
                else:
                    return key  # Return key if not found
            break

    if isinstance(value, str):
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return key


# Auto-detect language on import
set_language(detect_language())
