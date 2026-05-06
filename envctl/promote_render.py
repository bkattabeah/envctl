"""Rendering helpers for promote results."""

from envctl.promote import PromoteResult
from envctl.render import colorize


def render_promote_result(result: PromoteResult, *, color: bool = True) -> str:
    """Render a PromoteResult as a human-readable string."""
    lines = []

    header = f"Promote: {result.source!r} → {result.destination!r}"
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
