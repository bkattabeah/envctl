"""Render helpers for history results."""

from __future__ import annotations

from envctl.history import HistoryResult, KeyHistory
from envctl.render import colorize

_COL_KEY = 22
_COL_COUNT = 8
_COL_LAST = 26


def _header() -> str:
    key_h = "KEY".ljust(_COL_KEY)
    cnt_h = "CHANGES".ljust(_COL_COUNT)
    last_h = "LAST MODIFIED"
    sep = "-" * (_COL_KEY + _COL_COUNT + _COL_LAST)
    return f"{key_h}{cnt_h}{last_h}\n{sep}"


def render_history_table(result: HistoryResult) -> str:
    """Render a compact table of key change counts for a target."""
    lines = [
        colorize(f"History for target: {result.target}", bold=True),
        _header(),
    ]
    if not result.histories:
        lines.append(colorize("  (no recorded changes)", color="yellow"))
        return "\n".join(lines)

    for key in result.keys_changed():
        kh = result.histories[key]
        last = kh.last_changed.timestamp if kh.last_changed else "—"
        lines.append(
            f"{key.ljust(_COL_KEY)}{str(kh.change_count).ljust(_COL_COUNT)}{last}"
        )
    return "\n".join(lines)


def render_key_history(kh: KeyHistory) -> str:
    """Render a detailed timeline for a single key."""
    lines = [
        colorize(f"History for key '{kh.key}' in target '{kh.target}'", bold=True),
    ]
    if not kh.entries:
        lines.append(colorize("  (no recorded changes)", color="yellow"))
        return "\n".join(lines)

    for i, entry in enumerate(kh.entries, 1):
        action_str = colorize(entry.action.upper(), color="cyan")
        lines.append(f"  {i:>3}. [{entry.timestamp}]  {action_str}  (label: {entry.label or '—'})")
    return "\n".join(lines)


def render_history_not_found(target: str, key: str) -> str:
    return colorize(f"No history found for key '{key}' in target '{target}'.", color="yellow")
