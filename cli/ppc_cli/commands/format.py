"""
Format command
"""

from pathlib import Path

from ppc import loads, dumps

from ..i18n import t


def cmd_format(args) -> int:
    """Format a .ppc file."""
    path = Path(args.file)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse and re-dump
    config = loads(text)
    formatted = dumps(config)

    if args.write:
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(t("format.success", path=path))
    else:
        print(formatted)

    return 0
