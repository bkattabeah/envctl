"""Tests for envctl.encrypt and envctl.encrypt_store."""

import pytest

from envctl.encrypt import decrypt_env, encrypt_env


SAMPLE = {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}
PASS = "hunter2"


class TestEncryptDecrypt:
    def test_roundtrip(self):
        token = encrypt_env(SAMPLE, PASS)
        result = decrypt_env(token, PASS)
        assert result == SAMPLE

    def test_token_is_string(self):
        token = encrypt_env(SAMPLE, PASS)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_different_passphrases_produce_different_tokens(self):
        t1 = encrypt_env(SAMPLE, "pass1")
        t2 = encrypt_env(SAMPLE, "pass2")
        assert t1 != t2

    def test_wrong_passphrase_raises(self):
        token = encrypt_env(SAMPLE, PASS)
        with pytest.raises(ValueError, match="Decryption failed"):
            decrypt_env(token, "wrongpass")

    def test_empty_passphrase_encrypt_raises(self):
        with pytest.raises(ValueError, match="Passphrase"):
            encrypt_env(SAMPLE, "")

    def test_empty_passphrase_decrypt_raises(self):
        token = encrypt_env(SAMPLE, PASS)
        with pytest.raises(ValueError, match="Passphrase"):
            decrypt_env(token, "")

    def test_invalid_token_raises(self):
        with pytest.raises(ValueError):
            decrypt_env("not-valid-base64!!!", PASS)

    def test_empty_env_roundtrip(self):
        token = encrypt_env({}, PASS)
        assert decrypt_env(token, PASS) == {}

    def test_salting_makes_tokens_unique(self):
        t1 = encrypt_env(SAMPLE, PASS)
        t2 = encrypt_env(SAMPLE, PASS)
        # Different salts each call → different tokens
        assert t1 != t2
