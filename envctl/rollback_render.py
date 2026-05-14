"""Rendering helpers for RollbackResult."""

from __future__ import annotations

from envctl.rollback import RollbackResult
from envctl.render import colorize

_GREEN = "green"
_RED = "red"
_YELLOW = "yellow"
_CYAN = "cyan"
_BOLD = "bold"


def render_rollback_result(result: RollbackResult, *, mask: bool = False) -> str:
    lines: list[str] = []

    if not result.success:
        lines.append(colorize(f"✗ {result.summary()}", _RED))
        return "\n".join(lines)

    lines.append(
        colorize(f"✔ Rollback: ", _GREEN)
        + colorize(result.target, _BOLD)
        + "  →  "
        + colorize(result.rolled_back_to, _CYAN)
    )
    lines.append("")

    def _val(v: str) -> str:
        return "***" if mask else v

    if result.keys_added:
        lines.append(colorize(f"  Added ({len(result.keys_added)}):", _GREEN))
        for k in result.keys_added:
            lines.append(f"    + {k} = {_val(result.restored_env[k])}")

    if result.keys_removed:
        lines.append(colorize(f"  Removed ({len(result.keys_removed)}):", _RED))
        for k in result.keys_removed:
            lines.append(f"    - {k} = {_val(result.previous_env[k])}")

    if result.keys_changed:
        lines.append(colorize(f"  Changed ({len(result.keys_changed)}):", _YELLOW))
        for k in result.keys_changed:
            old = _val(result.previous_env[k])
            new = _val(result.restored_env[k])
            lines.append(f"    ~ {k}: {old!r} → {new!r}")

    if not (result.keys_added or result.keys_removed or result.keys_changed):
        lines.append(colorize("  No changes — environment already matches snapshot.", _CYAN))

    return "\n".join(lines)


def render_rollback_not_found(target: str, entry_id: str) -> str:
    return colorize(
        f"✗ Audit entry '{entry_id}' not found for target '{target}'.", _RED
    )
