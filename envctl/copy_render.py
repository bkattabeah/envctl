"""Rendering helpers for CopyResult."""

from envctl.copy import CopyResult
from envctl.render import colorize


def render_copy_result(result: CopyResult, *, mask: bool = True) -> str:
    lines: list[str] = []

    header = (
        f"Copy  {colorize(result.source, 'cyan', bold=True)}"
        f"  →  {colorize(result.destination, 'cyan', bold=True)}"
    )
    lines.append(header)
    lines.append("-" * 48)

    if result.copied:
        lines.append(colorize("  Copied:", "green", bold=True))
        for key, val in sorted(result.copied.items()):
            display = "***" if mask else val
            lines.append(f"    {colorize('+', 'green')} {key} = {display}")

    if result.skipped:
        lines.append(colorize("  Skipped (already exist):", "yellow", bold=True))
        for key in sorted(result.skipped):
            lines.append(f"    {colorize('~', 'yellow')} {key}")

    if result.missing:
        lines.append(colorize("  Not found in source:", "red", bold=True))
        for key in sorted(result.missing):
            lines.append(f"    {colorize('!', 'red')} {key}")

    lines.append("")
    lines.append(f"  Summary: {result.summary()}")

    return "\n".join(lines)
