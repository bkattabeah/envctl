"""Render lint results to the terminal."""

from __future__ import annotations

from envctl.lint import LintResult
from envctl.render import colorize

_SEV_COLOR = {
    'error': 'red',
    'warning': 'yellow',
}


def render_lint_result(result: LintResult, *, color: bool = True) -> str:
    """Return a human-readable string representation of a LintResult."""
    lines: list[str] = []

    if not result.issues:
        ok = "✔  " + result.summary()
        lines.append(colorize(ok, 'green') if color else ok)
        return "\n".join(lines)

    header = f"Lint report — {result.summary()}"
    lines.append(colorize(header, 'bold') if color else header)
    lines.append("")

    for issue in result.issues:
        sev = issue.severity
        tag = f"[{sev.upper()}]"
        col = _SEV_COLOR.get(sev, 'reset')
        tag_str = colorize(tag, col) if color else tag
        lines.append(f"  {tag_str}  {issue.key}: {issue.message}")

    lines.append("")
    if result.passed:
        verdict = colorize("Passed (warnings only).", 'yellow') if color else "Passed (warnings only)."
    else:
        verdict = colorize("Failed.", 'red') if color else "Failed."
    lines.append(verdict)

    return "\n".join(lines)
