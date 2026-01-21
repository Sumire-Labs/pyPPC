"""
Validate command
"""

from pathlib import Path

from ppc import load
from ppc.lexer import tokenize
from ppc.parser import parse
from ppc.exceptions import PPCError

from ..i18n import t


def cmd_validate(args) -> int:
    """Validate a .ppc file."""
    path = Path(args.file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Try to parse
        tokens = tokenize(text)
        ast = parse(text)

        # Try to load
        try:
            config = load(path)
        except PPCError as e:
            if "not found" not in str(e).lower():
                raise

        print(t("validate.success", path=path))
        return 0

    except PPCError as e:
        print(t("validate.error", path=path))
        print(f"  {e}")
        return 1
