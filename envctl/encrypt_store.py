"""Encrypted persistence layer wrapping EnvStore with passphrase protection."""

from pathlib import Path
from typing import Dict, List, Optional

from envctl.encrypt import decrypt_env, encrypt_env

_EXT = ".enc"


def _enc_path(base_dir: Path, target: str) -> Path:
    return base_dir / f"{target}{_EXT}"


def save_encrypted(
    base_dir: Path, target: str, env: Dict[str, str], passphrase: str
) -> None:
    """Encrypt and persist env vars for *target* under *base_dir*."""
    base_dir.mkdir(parents=True, exist_ok=True)
    token = encrypt_env(env, passphrase)
    _enc_path(base_dir, target).write_text(token, encoding="utf-8")


def load_encrypted(
    base_dir: Path, target: str, passphrase: str
) -> Dict[str, str]:
    """Load and decrypt env vars for *target*."""
    path = _enc_path(base_dir, target)
    if not path.exists():
        raise FileNotFoundError(f"No encrypted store for target '{target}'.")
    token = path.read_text(encoding="utf-8").strip()
    return decrypt_env(token, passphrase)


def list_encrypted_targets(base_dir: Path) -> List[str]:
    """Return target names that have an encrypted store."""
    if not base_dir.exists():
        return []
    return sorted(
        p.stem for p in base_dir.iterdir() if p.suffix == _EXT
    )


def delete_encrypted(base_dir: Path, target: str) -> bool:
    """Delete encrypted store for *target*. Returns True if it existed."""
    path = _enc_path(base_dir, target)
    if path.exists():
        path.unlink()
        return True
    return False
