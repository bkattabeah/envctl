"""Rendering helpers for encrypted-store operations."""

from typing import List

from envctl.render import colorize


def render_encrypted_targets(targets: List[str]) -> str:
    """Render a list of targets that have encrypted stores."""
    if not targets:
        return colorize("No encrypted targets found.", "yellow")
    lines = [colorize("Encrypted targets:", "bold")]
    for t in targets:
        lines.append(f"  {colorize('🔒', 'cyan')} {t}")
    return "\n".join(lines)


def render_encrypt_success(target: str) -> str:
    return (
        colorize("✔ ", "green")
        + f"Target "
        + colorize(target, "bold")
        + " encrypted and saved."
    )


def render_decrypt_success(target: str, key_count: int) -> str:
    return (
        colorize("✔ ", "green")
        + f"Target "
        + colorize(target, "bold")
        + f" decrypted — {key_count} key(s) loaded."
    )


def render_delete_encrypted(target: str, existed: bool) -> str:
    if existed:
        return colorize("✔ ", "green") + f"Encrypted store for '{target}' deleted."
    return colorize("! ", "yellow") + f"No encrypted store found for '{target}'."
