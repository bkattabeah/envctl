"""Render helpers for pipeline results."""
from __future__ import annotations

from envctl.pipeline import PipelineResult
from envctl.render import colorize

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"


def _val(v: str, mask: bool = False) -> str:
    return "***" if mask else v


def render_pipeline_result(result: PipelineResult, *, mask: bool = False) -> str:
    lines: list[str] = []

    if result.error:
        lines.append(f"{_RED}Pipeline error:{_RESET} {result.error}")
        return "\n".join(lines)

    header = f"{_BOLD}Pipeline:{_RESET} {_CYAN}{result.target}{_RESET}"
    lines.append(header)
    lines.append("")

    if result.steps_applied:
        lines.append(f"  {_GREEN}Steps applied:{_RESET}")
        for name in result.steps_applied:
            lines.append(f"    ✓ {name}")
    else:
        lines.append(f"  {_YELLOW}No steps applied.{_RESET}")

    if result.skipped:
        lines.append(f"  {_YELLOW}Steps skipped:{_RESET}")
        for name in result.skipped:
            lines.append(f"    ✗ {name}")

    added = [
        k for k in result.final_env if k not in result.initial_env
    ]
    removed = [
        k for k in result.initial_env if k not in result.final_env
    ]
    changed = [
        k for k in result.final_env
        if k in result.initial_env and result.final_env[k] != result.initial_env[k]
    ]

    lines.append("")
    if added:
        lines.append(f"  {_GREEN}Added:{_RESET} " + ", ".join(sorted(added)))
    if removed:
        lines.append(f"  {_RED}Removed:{_RESET} " + ", ".join(sorted(removed)))
    if changed:
        lines.append(f"  {_YELLOW}Changed:{_RESET} " + ", ".join(sorted(changed)))
    if not added and not removed and not changed:
        lines.append(f"  No keys changed.")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def render_pipeline_dry_run(result: PipelineResult) -> str:
    lines = [f"[dry-run] {result.summary()}"]
    return "\n".join(lines)
