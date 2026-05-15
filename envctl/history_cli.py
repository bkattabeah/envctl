"""CLI helpers for the history sub-command."""

from __future__ import annotations

import argparse
from typing import Optional

from envctl.history import build_history
from envctl.history_render import (
    render_history_table,
    render_key_history,
    render_history_not_found,
)


def add_history_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "history",
        help="Show change history for a target or specific key",
    )
    p.add_argument("target", help="Target name")
    p.add_argument(
        "--key", "-k", default=None, metavar="KEY",
        help="Limit output to a single key",
    )
    p.add_argument(
        "--base-dir", default=".envctl", metavar="DIR",
        help="Base directory for envctl data (default: .envctl)",
    )
    p.set_defaults(func=run_history)


def run_history(args: argparse.Namespace) -> None:
    base_dir: str = args.base_dir
    target: str = args.target
    key: Optional[str] = args.key

    result = build_history(base_dir, target, key_filter=key)

    if key:
        kh = result.for_key(key)
        if kh is None:
            print(render_history_not_found(target, key))
        else:
            print(render_key_history(kh))
    else:
        print(render_history_table(result))


def build_history_parser() -> argparse.ArgumentParser:
    """Stand-alone parser used for isolated testing."""
    parser = argparse.ArgumentParser(prog="envctl history")
    sub = parser.add_subparsers()
    add_history_subparser(sub)
    return parser
