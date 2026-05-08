"""CLI sub-commands for archive and restore."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envctl.env_store import EnvStore
from envctl.archive import archive_target, restore_archive
from envctl.archive_render import (
    render_archive_result,
    render_restore_result,
    render_archive_not_found,
)


def add_archive_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("archive", help="Archive a target to a bundle file")
    p.add_argument("target", help="Target name to archive")
    p.add_argument(
        "--dest",
        default=".",
        metavar="DIR",
        help="Directory to write the bundle (default: current dir)",
    )

    r = subparsers.add_parser("restore", help="Restore a target from a bundle file")
    r.add_argument("archive", help="Path to the .envbundle file")
    r.add_argument("target", help="Destination target name")
    r.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in the destination target",
    )


def run_archive(args: argparse.Namespace, store: EnvStore) -> int:
    result = archive_target(store, args.target, args.dest)
    print(render_archive_result(result))
    return 0


def run_restore(args: argparse.Namespace, store: EnvStore) -> int:
    if not Path(args.archive).exists():
        print(render_archive_not_found(args.archive), file=sys.stderr)
        return 1
    result = restore_archive(
        store,
        archive_path=args.archive,
        dest_target=args.target,
        overwrite=args.overwrite,
    )
    print(render_restore_result(result))
    return 0


def build_archive_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envctl-archive")
    sub = parser.add_subparsers(dest="command")
    add_archive_subparser(sub)
    return parser
