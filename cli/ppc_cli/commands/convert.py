"""
Convert commands (to-json, to-yaml)
"""

import json
from pathlib import Path
from typing import Any, Dict

from ppc import load

from ..i18n import t


def cmd_to_json(args) -> int:
    """Convert .ppc to JSON."""
    path = Path(args.file)
    config = load(path)
    data = config.to_dict()

    output = json.dumps(data, indent=args.indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(t("convert.success", path=args.output))
    else:
        print(output)

    return 0


def cmd_to_yaml(args) -> int:
    """Convert .ppc to YAML (simple implementation)."""
    path = Path(args.file)
    config = load(path)
    data = config.to_dict()

    output = _dict_to_yaml(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(t("convert.success", path=args.output))
    else:
        print(output)

    return 0


def _dict_to_yaml(data: Dict, indent: int = 0) -> str:
    """Simple dict to YAML converter (no external deps)."""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_dict_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    for k, v in item.items():
                        lines.append(f"{prefix}    {k}: {_yaml_value(v)}")
                else:
                    lines.append(f"{prefix}  - {_yaml_value(item)}")
        else:
            lines.append(f"{prefix}{key}: {_yaml_value(value)}")

    return "\n".join(lines)


def _yaml_value(value: Any) -> str:
    """Format value for YAML."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        if any(c in value for c in [":", "#", "'", '"', "\n"]):
            return f'"{value}"'
        return value
    return str(value)
