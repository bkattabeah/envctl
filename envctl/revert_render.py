"""Rendering helpers for RevertResult."""

from envctl.revert import RevertResult
from envctl.render import colorize

_GREEN = "green"
_RED = "red"
_YELLOW = "yellow"
_BOLD = "bold"


def render_revert_result(result: RevertResult, mask: bool = False) -> str:
    lines = []
    lines.append(
        colorize(f"Revert '{result.target}' → snapshot {result.snapshot_id}", _BOLD)
    )
    lines.append("")

    if result.keys_added:
        lines.append(colorize(f"  Added ({len(result.keys_added)}):", _GREEN))
        for k in result.keys_added:
            val = "***" if mask else result.reverted_env.get(k, "")
            lines.append(f"    + {k}={val}")

    if result.keys_removed:
        lines.append(colorize(f"  Removed ({len(result.keys_removed)}):", _RED))
        for k in result.keys_removed:
            val = "***" if mask else result.previous_env.get(k, "")
            lines.append(f"    - {k}={val}")

    if result.keys_changed:
        lines.append(colorize(f"  Changed ({len(result.keys_changed)}):", _YELLOW))
        for k in result.keys_changed:
            old = "***" if mask else result.previous_env.get(k, "")
            new = "***" if mask else result.reverted_env.get(k, "")
            lines.append(f"    ~ {k}: {old!r} → {new!r}")

    if not (result.keys_added or result.keys_removed or result.keys_changed):
        lines.append(colorize("  No changes — environment already matches snapshot.", _BOLD))

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)
