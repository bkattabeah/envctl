"""Render a CompareResult as a human-readable table."""

from typing import List, Optional
from envctl.compare import CompareResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"

COL_WIDTH = 22
KEY_WIDTH = 24


def _cell(value: Optional[str], divergent: bool, mask: bool = False) -> str:
    if value is None:
        return _DIM + "(absent)".ljust(COL_WIDTH) + _RESET
    display = "***" if mask else (value[:COL_WIDTH - 1] if len(value) >= COL_WIDTH else value)
    color = _RED if divergent else _GREEN
    return color + display.ljust(COL_WIDTH) + _RESET


def render_compare_table(result: CompareResult, mask_keys: Optional[List[str]] = None) -> str:
    mask_keys = set(mask_keys or [])
    lines = []

    header_parts = [_BOLD + "KEY".ljust(KEY_WIDTH) + _RESET]
    for t in result.targets:
        header_parts.append(_BOLD + _CYAN + t[:COL_WIDTH].ljust(COL_WIDTH) + _RESET)
    lines.append("  ".join(header_parts))

    sep_len = KEY_WIDTH + (COL_WIDTH + 2) * len(result.targets)
    lines.append("-" * sep_len)

    div_keys = set(result.divergent_keys())

    for key in result.all_keys:
        divergent = key in div_keys
        mask = key in mask_keys
        row = [(_YELLOW if divergent else "") + key.ljust(KEY_WIDTH) + (_RESET if divergent else "")]
        for t in result.targets:
            row.append(_cell(result.matrix[key][t], divergent, mask))
        lines.append("  ".join(row))

    lines.append("")
    lines.append(_summary_line(result))
    return "\n".join(lines)


def _summary_line(result: CompareResult) -> str:
    parts = [
        f"{len(result.all_keys)} keys total",
        f"{len(result.common_keys)} common",
        f"{len(result.divergent_keys())} divergent",
    ]
    unique_counts = ", ".join(
        f"{t}: {len(keys)} unique" for t, keys in result.unique_keys.items() if keys
    )
    if unique_counts:
        parts.append(unique_counts)
    return "Summary: " + " | ".join(parts)
