"""Rendering helpers for CloneResult."""

from envctl.clone import CloneResult
from envctl.render import colorize


def render_clone_result(result: CloneResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Clone: {result.source!r} -> {result.destination!r}"
    lines.append(colorize(header, "bold") if color else header)
    lines.append("")

    if result.keys_copied:
        label = colorize("Copied:", "green") if color else "Copied:"
        lines.append(f"  {label}")
        for key in result.keys_copied:
            lines.append(f"    + {key}")
    else:
        msg = colorize("  No keys copied.", "yellow") if color else "  No keys copied."
        lines.append(msg)

    if result.keys_skipped:
        lines.append("")
        label = colorize("Skipped:", "yellow") if color else "Skipped:"
        lines.append(f"  {label}")
        for key in result.keys_skipped:
            lines.append(f"    - {key}")

    lines.append("")
    summary = colorize(result.summary, "bold") if color else result.summary
    lines.append(summary)

    return "\n".join(lines)
