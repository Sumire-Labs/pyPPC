"""
Get command
"""

import json
import sys
from pathlib import Path

from ppc import load

from ..i18n import t


def cmd_get(args) -> int:
    """Get a value by key path."""
    path = Path(args.file)
    config = load(path)

    value = config.get_nested(args.key)
    if value is None:
        print(t("get.not_found", key=args.key), file=sys.stderr)
        return 1

    if hasattr(value, "to_dict"):
        print(json.dumps(value.to_dict(), indent=2, ensure_ascii=False))
    elif isinstance(value, (list, dict)):
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(value)

    return 0
