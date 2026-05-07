"""Rendering helpers for RenameResult."""

from envctl.rename import RenameResult
from envctl.render import colorize


def render_rename_result(result: RenameResult, *, color: bool = True) -> str:
    """Return a human-readable string describing a RenameResult."""
    lines: list[str] = []

    header = f"Rename: '{result.old_key}'  →  '{result.new_key}'"
    lines.append(colorize(header, "bold") if color else header)
    lines.append("")

    if result.affected_targets:
        label = colorize("  Updated", "green") if color else "  Updated"
        for t in result.affected_targets:
            lines.append(f"{label}  {t}")

    if result.skipped_targets:
        label = colorize("  Skipped", "yellow") if color else "  Skipped"
        for t in result.skipped_targets:
            lines.append(f"{label}  {t}  (key absent)")

    if result.collision_targets:
        label = colorize(" Conflict", "red") if color else " Conflict"
        for t in result.collision_targets:
            lines.append(
                f"{label}  {t}  ('{result.new_key}' already exists)"
            )

    if not (
        result.affected_targets
        or result.skipped_targets
        or result.collision_targets
    ):
        lines.append("  No targets processed.")

    return "\n".join(lines)
