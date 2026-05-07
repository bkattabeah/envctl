"""Rendering helpers for search results."""

from envctl.search import SearchResult
from envctl.render import colorize

_COL_TARGET = 14
_COL_KEY = 22
_COL_VALUE = 30
_COL_MATCH = 8


def _header() -> str:
    return (
        colorize(f"{'TARGET':<{_COL_TARGET}}", bold=True)
        + colorize(f"{'KEY':<{_COL_KEY}}", bold=True)
        + colorize(f"{'VALUE':<{_COL_VALUE}}", bold=True)
        + colorize(f"{'MATCH':<{_COL_MATCH}}", bold=True)
    )


def _separator() -> str:
    total = _COL_TARGET + _COL_KEY + _COL_VALUE + _COL_MATCH
    return "-" * total


def _match_color(matched_on: str) -> str:
    if matched_on == "key":
        return "cyan"
    if matched_on == "value":
        return "yellow"
    return "magenta"


def render_search_result(result: SearchResult, mask_values: bool = False) -> str:
    lines = []
    lines.append(f"Search: {colorize(result.query, bold=True)}")
    lines.append(_separator())

    if not result.has_matches:
        lines.append(colorize(result.summary(), color="yellow"))
        return "\n".join(lines)

    lines.append(_header())
    lines.append(_separator())

    current_target = None
    for match in result.matches:
        if match.target != current_target:
            current_target = match.target
        display_value = "***" if mask_values else match.value
        if len(display_value) > _COL_VALUE - 2:
            display_value = display_value[: _COL_VALUE - 5] + "..."
        color = _match_color(match.matched_on)
        row = (
            f"{match.target:<{_COL_TARGET}}"
            + f"{match.key:<{_COL_KEY}}"
            + f"{display_value:<{_COL_VALUE}}"
            + colorize(f"{match.matched_on:<{_COL_MATCH}}", color=color)
        )
        lines.append(row)

    lines.append(_separator())
    lines.append(result.summary())
    return "\n".join(lines)
