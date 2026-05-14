"""Rendering helpers for baseline output."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from envctl.baseline import BaselineResult
from envctl.render import colorize


def _fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def render_baseline_saved(result: BaselineResult) -> str:
    lines = [
        colorize(f"✔ Baseline saved: {result.baseline_id}", "green", bold=True),
        f"  Target  : {result.target}",
        f"  Keys    : {len(result.env)}",
        f"  Created : {_fmt_time(result.created_at)}",
    ]
    if result.label:
        lines.append(f"  Label   : {result.label}")
    return "\n".join(lines)


def render_baseline_list(results: list[BaselineResult], target: Optional[str] = None) -> str:
    if not results:
        scope = f" for target '{target}'" if target else ""
        return colorize(f"No baselines found{scope}.", "yellow")

    header_target = f" (target: {target})" if target else ""
    lines = [colorize(f"Baselines{header_target}:", "cyan", bold=True), ""]
    for r in results:
        label_part = f"  [{r.label}]" if r.label else ""
        lines.append(
            f"  {colorize(r.baseline_id, 'white', bold=True)}{label_part}"
        )
        lines.append(f"    Target : {r.target}  |  Keys: {len(r.env)}  |  {_fmt_time(r.created_at)}")
    return "\n".join(lines)


def render_baseline_deleted(baseline_id: str, found: bool) -> str:
    if found:
        return colorize(f"✔ Baseline '{baseline_id}' deleted.", "green")
    return colorize(f"✘ Baseline '{baseline_id}' not found.", "red")


def render_baseline_not_found(baseline_id: str) -> str:
    return colorize(f"✘ Baseline '{baseline_id}' does not exist.", "red")


def render_baseline_detail(result: BaselineResult) -> str:
    """Render a detailed view of a single baseline, including all env keys."""
    lines = [
        colorize(f"Baseline: {result.baseline_id}", "cyan", bold=True),
        f"  Target  : {result.target}",
        f"  Keys    : {len(result.env)}",
        f"  Created : {_fmt_time(result.created_at)}",
    ]
    if result.label:
        lines.append(f"  Label   : {result.label}")
    lines.append("")
    lines.append(colorize("  Environment variables:", "white", bold=True))
    for key in sorted(result.env):
        lines.append(f"    {colorize(key, 'yellow')} = {result.env[key]}")
    return "\n".join(lines)
