"""
Env command
"""

import os
import re
import sys
from pathlib import Path

from ..i18n import t


def cmd_env(args) -> int:
    """List required environment variables."""
    path = Path(args.file)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find all $env.VAR patterns
    env_vars = set(re.findall(r'\$env\.([A-Za-z_][A-Za-z0-9_]*)', text))
    secrets = set(re.findall(r'\$secret\.([A-Za-z_][A-Za-z0-9_]*)', text))

    if args.check:
        missing_env = []
        missing_secrets = []

        for var in env_vars:
            if var not in os.environ:
                missing_env.append(var)

        for var in secrets:
            if f"SECRET_{var}" not in os.environ:
                missing_secrets.append(var)

        if missing_env or missing_secrets:
            print(t("env.missing"), file=sys.stderr)
            for var in missing_env:
                print(f"  - {var}", file=sys.stderr)
            for var in missing_secrets:
                print(f"  - SECRET_{var}", file=sys.stderr)
            return 1
        else:
            print(t("env.all_set"))
            return 0
    else:
        if env_vars:
            print(t("env.header_env"))
            for var in sorted(env_vars):
                status = "[OK]" if var in os.environ else "[NG]"
                print(f"  {status} {var}")

        if secrets:
            print()
            print(t("env.header_secrets"))
            for var in sorted(secrets):
                status = "[OK]" if f"SECRET_{var}" in os.environ else "[NG]"
                print(f"  {status} SECRET_{var}")

        return 0
