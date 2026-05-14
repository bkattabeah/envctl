"""Rendering helpers for PatchResult."""

from __future__ import annotations

from envctl.patch import PatchResult
from envctl.render import colorize


def render_patch_result(result: PatchResult, *, mask: bool = False) -> str:
    lines: list[str] = []
    lines.append(colorize(f"Patch target: {result.target}", bold=True))

    def _val(v: str) -> str:
        return "****" if mask else v

    if result.added:
        lines.append(colorize("  Added:", fg="green"))
        for k, v in sorted(result.added.items()):
            lines.append(f"    + {k}={_val(v)}")

    if result.updated:
        lines.append(colorize("  Updated:", fg="yellow"))
        for k, v in sorted(result.updated.items()):
            lines.append(f"    ~ {k}={_val(v)}")

    if result.deleted:
        lines.append(colorize("  Deleted:", fg="red"))
        for k in sorted(result.deleted):
            lines.append(f"    - {k}")

    if result.skipped:
        lines.append(colorize("  Skipped (already exist):", fg="cyan"))
        for k in sorted(result.skipped):
            lines.append(f"    . {k}")

    if not (result.added or result.updated or result.deleted or result.skipped):
        lines.append(colorize("  No changes.", fg="cyan"))

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)
