"""Encryption helpers for securing sensitive env values at rest."""

import base64
import hashlib
import json
import os
from typing import Dict


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR data with a repeating key (lightweight, not AES — for demo use)."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt_env(env: Dict[str, str], passphrase: str) -> str:
    """Encrypt an env dict to a base64-encoded string using the passphrase."""
    if not passphrase:
        raise ValueError("Passphrase must not be empty.")
    raw = json.dumps(env, sort_keys=True).encode()
    salt = os.urandom(16)
    key = _derive_key(passphrase + salt.hex())
    encrypted = _xor_bytes(raw, key)
    payload = salt + encrypted
    return base64.b64encode(payload).decode()


def decrypt_env(token: str, passphrase: str) -> Dict[str, str]:
    """Decrypt a base64-encoded token back to an env dict."""
    if not passphrase:
        raise ValueError("Passphrase must not be empty.")
    try:
        payload = base64.b64decode(token.encode())
    except Exception as exc:
        raise ValueError("Invalid encrypted token.") from exc
    if len(payload) < 16:
        raise ValueError("Token too short to be valid.")
    salt = payload[:16]
    encrypted = payload[16:]
    key = _derive_key(passphrase + salt.hex())
    raw = _xor_bytes(encrypted, key)
    try:
        return json.loads(raw.decode())
    except Exception as exc:
        raise ValueError("Decryption failed — wrong passphrase or corrupted data.") from exc
