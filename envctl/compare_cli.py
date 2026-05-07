"""CLI helpers for the compare command."""

import argparse
import sys
from typing import List, Optional

from envctl.env_store import EnvStore
from envctl.compare import compare_targets
from envctl.compare_render import render_compare_table


def add_compare_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'compare' subcommand on an existing subparsers group."""
    p = subparsers.add_parser(
        "compare",
        help="Compare environment variables across two or more targets side-by-side.",
    )
    p.add_argument(
        "targets",
        nargs="+",
        metavar="TARGET",
        help="Two or more target names to compare.",
    )
    p.add_argument(
        "--mask",
        nargs="*",
        metavar="KEY",
        default=None,
        help="Keys whose values should be masked in output.",
    )
    p.add_argument(
        "--base-dir",
        default=None,
        metavar="DIR",
        help="Override the base directory for env storage.",
    )
    p.set_defaults(func=run_compare)


def run_compare(args: argparse.Namespace) -> int:
    """Execute the compare command; returns exit code."""
    if len(args.targets) < 2:
        print("error: compare requires at least two targets.", file=sys.stderr)
        return 1

    kwargs = {}
    if args.base_dir:
        kwargs["base_dir"] = args.base_dir

    store = EnvStore(**kwargs)

    try:
        result = compare_targets(store, args.targets)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(render_compare_table(result, mask_keys=args.mask))
    return 0


def build_compare_parser() -> argparse.ArgumentParser:
    """Standalone parser for testing the compare command in isolation."""
    parser = argparse.ArgumentParser(prog="envctl compare")
    subparsers = parser.add_subparsers()
    add_compare_subparser(subparsers)
    return parser
