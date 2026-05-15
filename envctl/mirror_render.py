"""Rendering helpers for MirrorResult."""

from __future__ import annotations

from envctl.mirror import MirrorResult
from envctl.render import colorize


def render_mirror_result(result: MirrorResult) -> str:
    lines: list[str] = []

    header = colorize(
        f"Mirror: {result.source} → {', '.join(result.destinations)}",
        bold=True,
    )
    lines.append(header)
    lines.append("")

    if not result.keys_mirrored:
        lines.append(colorize("  No keys to mirror.", color="yellow"))
        return "\n".join(lines)

    lines.append(colorize("  Keys mirrored:", bold=True))
    for k in result.keys_mirrored:
        lines.append(f"    {k}")

    if result.skipped:
        lines.append("")
        lines.append(colorize("  Skipped (already exist):", color="yellow", bold=True))
        for dest, ks in sorted(result.skipped.items()):
            lines.append(f"    [{dest}]: {', '.join(ks)}")

    lines.append("")
    lines.append(colorize(result.summary(), color="green"))
    return "\n".join(lines)


def render_mirror_source_not_found(source: str) -> str:
    return colorize(f"Error: source target '{source}' not found.", color="red")


def render_mirror_no_destinations() -> str:
    return colorize("Error: at least one destination target must be specified.", color="red")
