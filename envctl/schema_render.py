"""Rendering helpers for schema validation results."""

from __future__ import annotations

from envctl.render import colorize
from envctl.schema import SchemaResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def render_schema_result(result: SchemaResult, *, color: bool = True) -> str:
    lines: list[str] = []

    def c(text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if color else text

    header = c(f"Schema validation — {result.target}", _BOLD)
    lines.append(header)
    lines.append("-" * 44)

    if result.is_valid:
        lines.append(c("  ✔  All checks passed", _GREEN))
    else:
        if result.missing_required:
            lines.append(c("  Missing required keys:", _RED))
            for key in sorted(result.missing_required):
                lines.append(f"    - {key}")

        if result.pattern_violations:
            lines.append(c("  Pattern violations:", _RED))
            for key, val in sorted(result.pattern_violations.items()):
                lines.append(f"    - {key} = {c(val, _YELLOW)}")

        if result.disallowed_values:
            lines.append(c("  Disallowed values:", _RED))
            for key, val in sorted(result.disallowed_values.items()):
                lines.append(f"    - {key} = {c(val, _YELLOW)}")

    if result.unknown_keys:
        lines.append(c("  Unknown keys (strict mode):", _CYAN))
        for key in result.unknown_keys:
            lines.append(f"    ~ {key}")

    lines.append("")
    lines.append("  " + result.summary())
    return "\n".join(lines)


def render_schema_saved(schema_name: str, field_count: int, *, color: bool = True) -> str:
    msg = f"Schema '{schema_name}' saved ({field_count} field(s))"
    return f"\033[32m{msg}\033[0m" if color else msg


def render_schema_not_found(schema_name: str, *, color: bool = True) -> str:
    msg = f"Schema '{schema_name}' not found"
    return f"\033[31m{msg}\033[0m" if color else msg
