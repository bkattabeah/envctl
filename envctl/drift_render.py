"""Render helpers for DriftResult."""

from __future__ import annotations

from envctl.drift import DriftResult
from envctl.render import colorize

_W = 22


def _truncate(value: str, width: int = 32) -> str:
    return value if len(value) <= width else value[: width - 1] + "\u2026"


def render_drift_result(result: DriftResult, mask: bool = False) -> str:
    lines: list[str] = []
    lines.append(colorize(f"Drift report — {result.target} vs {result.baseline_id}", bold=True))

    def _val(v: str) -> str:
        return "****" if mask else _truncate(v)

    if not result.has_drift():
        lines.append(colorize("  No drift detected.", color="green"))
        return "\n".join(lines)

    if result.added:
        lines.append(colorize("  Added:", bold=True))
        for k, v in sorted(result.added.items()):
            lines.append(colorize(f"    + {k:<{_W}} {_val(v)}", color="green"))

    if result.removed:
        lines.append(colorize("  Removed:", bold=True))
        for k, v in sorted(result.removed.items()):
            lines.append(colorize(f"    - {k:<{_W}} {_val(v)}", color="red"))

    if result.changed:
        lines.append(colorize("  Changed:", bold=True))
        for k, (old, new) in sorted(result.changed.items()):
            lines.append(colorize(f"    ~ {k:<{_W}} {_val(old)} -> {_val(new)}", color="yellow"))

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def render_drift_clean(target: str, baseline_id: str) -> str:
    return colorize(
        f"\u2714 {target}: no drift against baseline {baseline_id}.",
        color="green",
    )


def render_drift_not_found(target: str) -> str:
    return colorize(f"No baseline found for target '{target}'.", color="red")
