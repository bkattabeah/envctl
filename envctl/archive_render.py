"""Rendering helpers for archive/restore results."""

from __future__ import annotations

from envctl.archive import ArchiveResult
from envctl.render import colorize


def render_archive_result(result: ArchiveResult) -> str:
    lines: list[str] = []
    header = colorize(f"Archived: {result.target}", bold=True)
    lines.append(header)
    lines.append(f"  Bundle : {result.archive_path}")
    lines.append(f"  Keys   : {len(result.keys_archived)}")
    if result.keys_archived:
        for k in result.keys_archived:
            lines.append(f"    • {k}")
    return "\n".join(lines)


def render_restore_result(result: ArchiveResult) -> str:
    lines: list[str] = []
    header = colorize(
        f"Restored: {result.target} → {result.restored_to}", bold=True
    )
    lines.append(header)
    lines.append(f"  Source : {result.archive_path}")
    lines.append(f"  Keys   : {len(result.keys_archived)}")
    if result.overwritten_keys:
        ow = colorize("overwritten", color="yellow")
        lines.append(f"  {ow}  : {', '.join(sorted(result.overwritten_keys))}")
    else:
        lines.append("  No existing keys were overwritten.")
    return "\n".join(lines)


def render_archive_not_found(path: str) -> str:
    return colorize(f"Error: archive not found: {path}", color="red")
