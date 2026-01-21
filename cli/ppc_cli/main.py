"""
pyPPC CLI - Main entry point
"""

import argparse
import sys

from ppc import __version__ as lib_version
from ppc.exceptions import PPCError

from . import __version__ as cli_version
from .i18n import t, set_language, LANGUAGES
from .commands import (
    cmd_validate,
    cmd_format,
    cmd_to_json,
    cmd_to_yaml,
    cmd_get,
    cmd_env,
    cmd_init,
)


def main():
    """Main entry point for CLI."""
    # Pre-parse for language option
    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            set_language(sys.argv[idx + 1])

    parser = argparse.ArgumentParser(
        prog="ppc",
        description=t("app.description"),
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pyPPC {lib_version} (CLI {cli_version})",
    )
    parser.add_argument(
        "--lang",
        choices=list(LANGUAGES.keys()),
        help=t("args.lang"),
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate
    validate_parser = subparsers.add_parser(
        "validate",
        help=t("commands.validate"),
    )
    validate_parser.add_argument("file", help=t("args.file"))

    # format
    format_parser = subparsers.add_parser(
        "format",
        help=t("commands.format"),
    )
    format_parser.add_argument("file", help=t("args.file"))
    format_parser.add_argument(
        "-w", "--write",
        action="store_true",
        help=t("args.write"),
    )

    # to-json
    json_parser = subparsers.add_parser(
        "to-json",
        help=t("commands.to_json"),
    )
    json_parser.add_argument("file", help=t("args.file"))
    json_parser.add_argument(
        "-o", "--output",
        help=t("args.output"),
    )
    json_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help=t("args.indent"),
    )

    # to-yaml
    yaml_parser = subparsers.add_parser(
        "to-yaml",
        help=t("commands.to_yaml"),
    )
    yaml_parser.add_argument("file", help=t("args.file"))
    yaml_parser.add_argument(
        "-o", "--output",
        help=t("args.output"),
    )

    # get
    get_parser = subparsers.add_parser(
        "get",
        help=t("commands.get"),
    )
    get_parser.add_argument("file", help=t("args.file"))
    get_parser.add_argument("key", help=t("args.key"))

    # env
    env_parser = subparsers.add_parser(
        "env",
        help=t("commands.env"),
    )
    env_parser.add_argument("file", help=t("args.file"))
    env_parser.add_argument(
        "--check",
        action="store_true",
        help=t("args.check"),
    )

    # init
    init_parser = subparsers.add_parser(
        "init",
        help=t("commands.init"),
    )
    init_parser.add_argument(
        "-o", "--output",
        default="config.ppc",
        help=t("args.output"),
    )
    init_parser.add_argument(
        "-t", "--template",
        choices=["minimal", "bot", "web"],
        default="minimal",
        help=t("args.template"),
    )

    args = parser.parse_args()

    # Apply language if specified
    if args.lang:
        set_language(args.lang)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        exit_code = 0

        if args.command == "validate":
            exit_code = cmd_validate(args)
        elif args.command == "format":
            exit_code = cmd_format(args)
        elif args.command == "to-json":
            exit_code = cmd_to_json(args)
        elif args.command == "to-yaml":
            exit_code = cmd_to_yaml(args)
        elif args.command == "get":
            exit_code = cmd_get(args)
        elif args.command == "env":
            exit_code = cmd_env(args)
        elif args.command == "init":
            exit_code = cmd_init(args)

        sys.exit(exit_code)

    except PPCError as e:
        print(t("errors.parse_error", message=str(e)), file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(t("errors.file_not_found", path=str(e)), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(t("errors.unknown_error", message=str(e)), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
