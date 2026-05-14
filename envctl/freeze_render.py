"""Rendering helpers for freeze/unfreeze results."""

from __future__ import annotations

from typing import List, Optional

from envctl.freeze import FreezeResult
from envctl.render import colorize

_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def render_freeze_result(result: FreezeResult) -> str:
    icon = "\u2744" if result.frozen else "\u2600"
    color = _CYAN if result.frozen else _GREEN
    action = "Frozen" if result.frozen else "Unfrozen"
    label_part = f"  label={result.label}" if result.label else ""
    target_str = colorize(result.target, bold=True)
    return (
        f"{color}{icon} {action}:{_RESET} {target_str}\n"
        f"  timestamp={result.timestamp}{label_part}"
    )


def render_unfreeze_not_found(target: str) -> str:
    return f"{_YELLOW}\u26a0 Target '{target}' is not frozen.{_RESET}"


def render_frozen_list(results: List[FreezeResult]) -> str:
    if not results:
        return f"{_YELLOW}No frozen targets.{_RESET}"

    header = f"{_BOLD}Frozen targets:{_RESET}"
    rows = []
    for r in results:
        label_part = f"  ({r.label})" if r.label else ""
        rows.append(f"  {_CYAN}\u2744{_RESET} {colorize(r.target, bold=True)}{label_part}  {r.timestamp}")
    return "\n".join([header] + rows)


def render_freeze_guard(target: str) -> str:
    """Message shown when a write operation is blocked by a freeze."""
    return (
        f"{_YELLOW}\u274c Operation blocked:{_RESET} "
        f"target {colorize(target, bold=True)} is frozen.\n"
        f"  Run `envctl unfreeze {target}` to allow changes."
    )
