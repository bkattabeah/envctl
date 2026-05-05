"""Command-line interface for envctl."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envctl.env_store import EnvStore
from envctl.export import export_env, import_dotenv, ExportFormat
from envctl.render import render_diff_table, render_env_table
from envctl.diff import diff_envs


DEFAULT_STORE = Path.home() / ".envctl" / "store"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envctl",
        description="Manage and diff environment variable sets across deployment targets.",
    )
    parser.add_argument("--store", default=str(DEFAULT_STORE), help="Path to env store directory")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all targets")

    # show
    show = sub.add_parser("show", help="Show env vars for a target")
    show.add_argument("target")
    show.add_argument("--format", choices=["dotenv", "json", "shell"], default="dotenv")

    # set
    set_p = sub.add_parser("set", help="Set a key=value pair for a target")
    set_p.add_argument("target")
    set_p.add_argument("pair", help="KEY=VALUE")

    # delete
    del_p = sub.add_parser("delete", help="Delete a target")
    del_p.add_argument("target")

    # diff
    diff_p = sub.add_parser("diff", help="Diff two targets")
    diff_p.add_argument("target_a")
    diff_p.add_argument("target_b")
    diff_p.add_argument("--mask", action="store_true", help="Mask secret values")

    # import
    imp = sub.add_parser("import", help="Import a .env file into a target")
    imp.add_argument("target")
    imp.add_argument("file", help="Path to .env file")

    # export
    exp = sub.add_parser("export", help="Export a target to stdout")
    exp.add_argument("target")
    exp.add_argument("--format", choices=["dotenv", "json", "shell"], default="dotenv")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = EnvStore(args.store)

    if args.command == "list":
        targets = store.list_targets()
        print("\n".join(targets) if targets else "(no targets)")

    elif args.command == "show":
        env = store.load(args.target)
        print(render_env_table(env, title=args.target), end="")

    elif args.command == "set":
        if "=" not in args.pair:
            print("Error: pair must be KEY=VALUE", file=sys.stderr)
            return 1
        key, _, value = args.pair.partition("=")
        env = store.load(args.target)
        env[key.strip()] = value
        store.save(args.target, env)
        print(f"Set {key.strip()} for target '{args.target}'.")

    elif args.command == "delete":
        store.delete(args.target)
        print(f"Deleted target '{args.target}'.")

    elif args.command == "diff":
        env_a = store.load(args.target_a)
        env_b = store.load(args.target_b)
        result = diff_envs(env_a, env_b)
        print(render_diff_table(result.added, result.removed, result.changed, mask_secrets=args.mask), end="")

    elif args.command == "import":
        text = Path(args.file).read_text()
        env = import_dotenv(text)
        store.save(args.target, env)
        print(f"Imported {len(env)} variables into target '{args.target}'.")

    elif args.command == "export":
        env = store.load(args.target)
        print(export_env(env, fmt=args.format), end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
