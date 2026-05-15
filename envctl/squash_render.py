"""Rendering helpers for SquashResult."""
from __future__ import annotations

from envctl.squash import SquashResult
from envctl.render import colorize

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def render_squash_result(result: SquashResult, *, no_color: bool = False) -> str:
    def c(text: str, code: str) -> str:
        return text if no_color else f"{code}{text}{_RESET}"

    lines = [
        c(f"Squash → {result.destination}", _BOLD),
        "",
    ]

    if result.sources:
        lines.append(c("Sources merged:", _CYAN))
        for src in result.sources:
            lines.append(f"  {src}")
    else:
        lines.append(c("  (no sources loaded)", _YELLOW))

    lines.append("")
    lines.append(c(f"Total keys: {len(result.env)}", _GREEN))

    if result.overwritten_keys:
        lines.append("")
        lines.append(c("Overwritten keys (last-wins):", _YELLOW))
        for k in result.overwritten_keys:
            lines.append(f"  {k}")

    if result.skipped_sources:
        lines.append("")
        lines.append(c("Skipped (not found):", _YELLOW))
        for s in result.skipped_sources:
            lines.append(f"  {s}")

    return "\n".join(lines)


def render_squash_empty(destination: str, *, no_color: bool = False) -> str:
    msg = f"No sources provided — '{destination}' was not modified."
    if no_color:
        return msg
    return f"{_YELLOW}{msg}{_RESET}"
