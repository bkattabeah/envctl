"""Rendering helpers for audit log output."""

import datetime
from typing import List

from envctl.audit import AuditEntry
from envctl.render import colorize

_ACTION_COLORS = {
    "set": "\033[32m",       # green
    "delete": "\033[31m",    # red
    "import": "\033[34m",    # blue
    "snapshot": "\033[33m",  # yellow
}


def _fmt_time(ts: float) -> str:
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _fmt_action(action: str) -> str:
    color = _ACTION_COLORS.get(action, "")
    reset = "\033[0m" if color else ""
    return f"{color}{action:<10}{reset}"


def render_audit_log(entries: List[AuditEntry], use_color: bool = True) -> str:
    """Render a list of audit entries as a formatted table string."""
    if not entries:
        return "No audit entries found.\n"

    header = f"{'TIMESTAMP':<25} {'ACTION':<10} {'TARGET':<20} {'KEYS'}"
    divider = "-" * 80
    lines = []

    if use_color:
        lines.append(colorize(header, bold=True))
    else:
        lines.append(header)
    lines.append(divider)

    for entry in entries:
        ts_str = _fmt_time(entry.timestamp)
        keys_str = ", ".join(entry.keys) if entry.keys else "(none)"
        label_str = f"  [{entry.label}]" if entry.label else ""
        action_str = _fmt_action(entry.action) if use_color else f"{entry.action:<10}"
        line = f"{ts_str:<25} {action_str} {entry.target:<20} {keys_str}{label_str}"
        lines.append(line)

    return "\n".join(lines) + "\n"
