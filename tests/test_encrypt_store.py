"""Tests for envctl.encrypt_store."""

import pytest

from envctl.encrypt_store import (
    delete_encrypted,
    list_encrypted_targets,
    load_encrypted,
    save_encrypted,
)

SAMPLE = {"DB_URL": "postgres://localhost/db", "SECRET": "s3cr3t"}
PASS = "mypassphrase"


@pytest.fixture()
def enc_dir(tmp_path):
    return tmp_path / "enc_store"


class TestEncryptStore:
    def test_save_and_load(self, enc_dir):
        save_encrypted(enc_dir, "prod", SAMPLE, PASS)
        result = load_encrypted(enc_dir, "prod", PASS)
        assert result == SAMPLE

    def test_creates_directory(self, enc_dir):
        assert not enc_dir.exists()
        save_encrypted(enc_dir, "staging", SAMPLE, PASS)
        assert enc_dir.exists()

    def test_file_extension_is_enc(self, enc_dir):
        save_encrypted(enc_dir, "dev", SAMPLE, PASS)
        files = list(enc_dir.iterdir())
        assert all(f.suffix == ".enc" for f in files)

    def test_load_missing_target_raises(self, enc_dir):
        enc_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="prod"):
            load_encrypted(enc_dir, "prod", PASS)

    def test_list_targets_empty(self, enc_dir):
        enc_dir.mkdir()
        assert list_encrypted_targets(enc_dir) == []

    def test_list_targets_returns_names(self, enc_dir):
        for t in ("alpha", "beta", "gamma"):
            save_encrypted(enc_dir, t, SAMPLE, PASS)
        assert list_encrypted_targets(enc_dir) == ["alpha", "beta", "gamma"]

    def test_delete_existing(self, enc_dir):
        save_encrypted(enc_dir, "prod", SAMPLE, PASS)
        removed = delete_encrypted(enc_dir, "prod")
        assert removed is True
        assert list_encrypted_targets(enc_dir) == []

    def test_delete_nonexistent(self, enc_dir):
        enc_dir.mkdir()
        removed = delete_encrypted(enc_dir, "ghost")
        assert removed is False

    def test_wrong_passphrase_on_load_raises(self, enc_dir):
        save_encrypted(enc_dir, "prod", SAMPLE, PASS)
        with pytest.raises(ValueError):
            load_encrypted(enc_dir, "prod", "badpass")
