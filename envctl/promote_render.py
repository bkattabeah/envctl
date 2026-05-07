"""Rendering helpers for promote results."""

from envctl.promote import PromoteResult
from envctl.render import colorize


def _render_key_section(
    keys: set,
    label_plain: str,
    label_color: str,
    color: bool,
    lines: list,
) -> None:
    """Append a labeled section of keys to lines, if any keys exist."""
    if not keys:
        return
    label = colorize(label_color, label_color.split()[1]) if color else label_plain
    label = colorize(label_plain, label_color) if color else label_plain
    for key in sorted(keys):
        lines.append(f"{label}: {key}")


def render_promote_result(result: PromoteResult, *, color: bool = True) -> str:
    """Render a PromoteResult as a human-readable string.

    Args:
        result: The PromoteResult to render.
        color: Whether to include ANSI color codes in the output.

    Returns:
        A formatted, human-readable string summarising the promote operation.
    """
    lines = []

    header = f"Promote: {result.source!r} \u2192 {result.destination!r}"
    lines.append(colorize(header, "bold") if color else header)
    lines.append("")

    if result.promoted_keys:
        label = colorize("  + promoted", "green") if color else "  + promoted"
        for key in sorted(result.promoted_keys):
            lines.append(f"{label}: {key}")

    if result.overwritten_keys:
        label = colorize("  ~ overwritten", "yellow") if color else "  ~ overwritten"
        for key in sorted(result.overwritten_keys):
            lines.append(f"{label}: {key}")

    if result.skipped_keys:
        label = colorize("  - skipped", "cyan") if color else "  - skipped"
        for key in sorted(result.skipped_keys):
            lines.append(f"{label}: {key}")

    lines.append("")
    summary_text = f"Summary: {result.summary}"
    lines.append(colorize(summary_text, "bold") if color else summary_text)

    return "\n".join(lines)
