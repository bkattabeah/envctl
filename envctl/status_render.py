"""Render helpers for StatusResult."""

from __future__ import annotations

from envctl.status import StatusResult, TargetStatus
from envctl.render import colorize

_HEALTH_COLOR = {
    "ok": "green",
    "warn": "yellow",
    "error": "red",
}

_COL_WIDTHS = {
    "target": 20,
    "keys": 6,
    "frozen": 7,
    "health": 7,
    "issues": 22,
    "tags": 20,
}


def _pad(text: str, width: int) -> str:
    return text[:width].ljust(width)


def _render_row(s: TargetStatus) -> str:
    health_label = s.health.upper()
    color = _HEALTH_COLOR.get(s.health, "white")
    health_cell = colorize(health_label, color)

    issues = []
    if s.lint_errors:
        issues.append(f"{s.lint_errors}E")
    if s.lint_warnings:
        issues.append(f"{s.lint_warnings}W")
    issues_str = ", ".join(issues) if issues else "-"

    frozen_str = colorize("yes", "cyan") if s.frozen else "-"
    tags_str = ", ".join(s.tags) if s.tags else "-"

    return "  ".join([
        _pad(s.target, _COL_WIDTHS["target"]),
        _pad(str(s.key_count), _COL_WIDTHS["keys"]),
        _pad(frozen_str, _COL_WIDTHS["frozen"] + 9),  # extra for ANSI
        _pad(health_cell, _COL_WIDTHS["health"] + 9),
        _pad(issues_str, _COL_WIDTHS["issues"]),
        tags_str,
    ])


def render_status_table(result: StatusResult) -> str:
    if not result.statuses:
        return "No targets found."

    header = "  ".join([
        _pad("TARGET", _COL_WIDTHS["target"]),
        _pad("KEYS", _COL_WIDTHS["keys"]),
        _pad("FROZEN", _COL_WIDTHS["frozen"]),
        _pad("HEALTH", _COL_WIDTHS["health"]),
        _pad("ISSUES", _COL_WIDTHS["issues"]),
        "TAGS",
    ])
    sep = "-" * 80
    rows = [_render_row(s) for s in result.statuses]
    lines = [header, sep] + rows + [sep, result.summary]
    return "\n".join(lines)


def render_status_single(s: TargetStatus) -> str:
    color = _HEALTH_COLOR.get(s.health, "white")
    lines = [
        f"Target : {s.target}",
        f"Keys   : {s.key_count}",
        f"Frozen : {'yes' if s.frozen else 'no'}",
        f"Health : {colorize(s.health.upper(), color)}",
        f"Errors : {s.lint_errors}",
        f"Warns  : {s.lint_warnings}",
        f"Tags   : {', '.join(s.tags) if s.tags else '-'}",
    ]
    return "\n".join(lines)
