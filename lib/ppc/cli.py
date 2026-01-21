"""
pyPPC - Command Line Interface
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import load, loads, dumps, __version__
from .lexer import tokenize, TokenType
from .parser import parse
from .exceptions import PPCError


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="ppc",
        description="pyPPC - A human-readable configuration format",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pyPPC {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a .ppc file",
    )
    validate_parser.add_argument("file", help="Path to .ppc file")

    # format
    format_parser = subparsers.add_parser(
        "format",
        help="Format a .ppc file",
    )
    format_parser.add_argument("file", help="Path to .ppc file")
    format_parser.add_argument(
        "-w", "--write",
        action="store_true",
        help="Write result back to file",
    )

    # to-json
    json_parser = subparsers.add_parser(
        "to-json",
        help="Convert .ppc to JSON",
    )
    json_parser.add_argument("file", help="Path to .ppc file")
    json_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)",
    )
    json_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default: 2)",
    )

    # to-yaml
    yaml_parser = subparsers.add_parser(
        "to-yaml",
        help="Convert .ppc to YAML",
    )
    yaml_parser.add_argument("file", help="Path to .ppc file")
    yaml_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)",
    )

    # get
    get_parser = subparsers.add_parser(
        "get",
        help="Get a value by key path",
    )
    get_parser.add_argument("file", help="Path to .ppc file")
    get_parser.add_argument("key", help="Key path (e.g., bot.token)")

    # env
    env_parser = subparsers.add_parser(
        "env",
        help="List required environment variables",
    )
    env_parser.add_argument("file", help="Path to .ppc file")
    env_parser.add_argument(
        "--check",
        action="store_true",
        help="Check if all env vars are set",
    )

    # init
    init_parser = subparsers.add_parser(
        "init",
        help="Create a new .ppc file from template",
    )
    init_parser.add_argument(
        "-o", "--output",
        default="config.ppc",
        help="Output file (default: config.ppc)",
    )
    init_parser.add_argument(
        "-t", "--template",
        choices=["minimal", "bot", "web"],
        default="minimal",
        help="Template type (default: minimal)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "validate":
            cmd_validate(args)
        elif args.command == "format":
            cmd_format(args)
        elif args.command == "to-json":
            cmd_to_json(args)
        elif args.command == "to-yaml":
            cmd_to_yaml(args)
        elif args.command == "get":
            cmd_get(args)
        elif args.command == "env":
            cmd_env(args)
        elif args.command == "init":
            cmd_init(args)
    except PPCError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    """Validate a .ppc file."""
    path = Path(args.file)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Try to parse
    tokens = tokenize(text)
    ast = parse(text)

    # Try to load (with dummy env)
    try:
        config = load(path)
    except PPCError as e:
        if "not found" not in str(e).lower():
            raise

    print(f"[OK] {path} is valid")


def cmd_format(args):
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
        print(f"[OK] Formatted {path}")
    else:
        print(formatted)


def cmd_to_json(args):
    """Convert .ppc to JSON."""
    path = Path(args.file)
    config = load(path)
    data = config.to_dict()

    output = json.dumps(data, indent=args.indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[OK] Saved to {args.output}")
    else:
        print(output)


def cmd_to_yaml(args):
    """Convert .ppc to YAML (simple implementation)."""
    path = Path(args.file)
    config = load(path)
    data = config.to_dict()

    output = dict_to_yaml(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[OK] Saved to {args.output}")
    else:
        print(output)


def dict_to_yaml(data: Dict, indent: int = 0) -> str:
    """Simple dict to YAML converter (no external deps)."""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(dict_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    for k, v in item.items():
                        lines.append(f"{prefix}    {k}: {yaml_value(v)}")
                else:
                    lines.append(f"{prefix}  - {yaml_value(item)}")
        else:
            lines.append(f"{prefix}{key}: {yaml_value(value)}")

    return "\n".join(lines)


def yaml_value(value: Any) -> str:
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


def cmd_get(args):
    """Get a value by key path."""
    path = Path(args.file)
    config = load(path)

    value = config.get_nested(args.key)
    if value is None:
        print(f"Key not found: {args.key}", file=sys.stderr)
        sys.exit(1)

    if hasattr(value, "to_dict"):
        print(json.dumps(value.to_dict(), indent=2, ensure_ascii=False))
    elif isinstance(value, (list, dict)):
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(value)


def cmd_env(args):
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
            print("Missing environment variables:", file=sys.stderr)
            for var in missing_env:
                print(f"  - {var}", file=sys.stderr)
            for var in missing_secrets:
                print(f"  - SECRET_{var}", file=sys.stderr)
            sys.exit(1)
        else:
            print("[OK] All environment variables are set")
    else:
        if env_vars:
            print("Environment variables:")
            for var in sorted(env_vars):
                status = "[OK]" if var in os.environ else "[NG]"
                print(f"  {status} {var}")

        if secrets:
            print("\nSecrets (SECRET_*):")
            for var in sorted(secrets):
                status = "[OK]" if f"SECRET_{var}" in os.environ else "[NG]"
                print(f"  {status} SECRET_{var}")


def cmd_init(args):
    """Create a new .ppc file from template."""
    templates = {
        "minimal": '''# Configuration
>> app
  name = "myapp"
  debug :: bool = false
''',
        "bot": '''# Discord Bot Configuration
>> bot
  token :: str = $env.DISCORD_TOKEN
  prefix :: str = "!"
  description = "My Discord Bot"

>> database
  host = "localhost"
  port :: int = 5432
  password = $secret.DB_PASS

>> cogs
  enabled = ["music", "moderation", "fun"]

>> @when $env.ENV == "dev"
  >> bot
    debug = true
    prefix = "??"
''',
        "web": '''# Web Application Configuration
>> server
  host = "0.0.0.0"
  port :: int = $env.PORT ?? 8080
  debug :: bool = false

>> database
  url = $env.DATABASE_URL ?? "sqlite:///app.db"

>> session
  secret_key = $secret.SESSION_KEY
  expire :: int = 3600

>> @when $env.ENV == "dev"
  >> server
    debug = true
    host = "127.0.0.1"
''',
    }

    output = Path(args.output)
    if output.exists():
        print(f"Error: {output} already exists", file=sys.stderr)
        sys.exit(1)

    with open(output, "w", encoding="utf-8") as f:
        f.write(templates[args.template])

    print(f"[OK] Created {output}")


if __name__ == "__main__":
    main()
