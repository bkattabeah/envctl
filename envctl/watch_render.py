"""Rendering helpers for watch events."""

from __future__ import annotations

import datetime
from typing import List

from envctl.watch import WatchEvent
from envctl.render import colorize

_GREEN = "green"
_RED = "red"
_YELLOW = "yellow"
_CYAN = "cyan"


def _fmt_time(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")


def render_watch_event(event: WatchEvent, mask_values: bool = False) -> str:
    """Render a single WatchEvent to a human-readable string.

    Args:
        event: The WatchEvent to render.
        mask_values: If True, replace variable values with '***'.

    Returns:
        A formatted, colorized string representation of the event.
    """
    lines: List[str] = []
    header = colorize(
        f"[{_fmt_time(event.timestamp)}] {event.target}: {event.summary()}",
        color=_CYAN,
        bold=True,
    )
    lines.append(header)

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for key, val in sorted(event.added.items()):
        lines.append(colorize(f"  + {key}={_val(val)}", color=_GREEN))

    for key, val in sorted(event.removed.items()):
        lines.append(colorize(f"  - {key}={_val(val)}", color=_RED))

    for key, old, new in sorted(event.changed):
        old_str = colorize(_val(old), color=_RED)
        new_str = colorize(_val(new), color=_GREEN)
        lines.append(f"  ~ {key}: {old_str} -> {new_str}")

    return "\n".join(lines)


def render_watch_summary(events: List[WatchEvent]) -> str:
    """Render a summary line after a watch session ends.

    Args:
        events: All WatchEvents collected during the session.

    Returns:
        A colorized summary string indicating the number of events and changes.
    """
    if not events:
        return colorize("Watch complete. No changes detected.", color=_CYAN)
    total_changes = sum(
        len(e.added) + len(e.removed) + len(e.changed) for e in events
    )
    return colorize(
        f"Watch complete. {len(events)} event(s), {total_changes} total change(s).",
        color=_YELLOW,
        bold=True,
    )
