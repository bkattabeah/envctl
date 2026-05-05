"""Terminal rendering helpers for envctl output."""

from __future__ import annotations

from typing import Dict, Optional

ANSI_RESET = "\033[0m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_BOLD = "\033[1m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    prefix = (ANSI_BOLD if bold else "") + color
    return f"{prefix}{text}{ANSI_RESET}"


def render_diff_table(
    added: Dict[str, str],
    removed: Dict[str, str],
    changed: Dict[str, tuple],
    mask_secrets: bool = False,
) -> str:
    """Render a human-readable diff table for terminal output."""
    lines: list[str] = []

    def _val(v: str) -> str:
        return "***" if mask_secrets else v

    if added:
        lines.append(colorize("Added:", ANSI_GREEN, bold=True))
        for k, v in sorted(added.items()):
            lines.append(colorize(f"  + {k}={_val(v)}", ANSI_GREEN))

    if removed:
        lines.append(colorize("Removed:", ANSI_RED, bold=True))
        for k, v in sorted(removed.items()):
            lines.append(colorize(f"  - {k}={_val(v)}", ANSI_RED))

    if changed:
        lines.append(colorize("Changed:", ANSI_YELLOW, bold=True))
        for k, (old, new) in sorted(changed.items()):
            lines.append(colorize(f"  ~ {k}", ANSI_YELLOW))
            lines.append(colorize(f"      before: {_val(old)}", ANSI_RED))
            lines.append(colorize(f"      after:  {_val(new)}", ANSI_GREEN))

    if not lines:
        lines.append(colorize("No differences found.", ANSI_CYAN))

    return "\n".join(lines) + "\n"


def render_env_table(env: Dict[str, str], title: Optional[str] = None) -> str:
    """Render a single env dict as a simple key=value table."""
    lines: list[str] = []
    if title:
        lines.append(colorize(title, ANSI_BOLD + ANSI_CYAN))
    if not env:
        lines.append("  (empty)")
    else:
        for k, v in sorted(env.items()):
            lines.append(f"  {k}={v}")
    return "\n".join(lines) + "\n"
