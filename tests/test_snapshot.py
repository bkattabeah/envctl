"""Tests for envctl.snapshot."""

import pytest

from envctl.snapshot import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
)

SAMPLE_ENV = {"APP_ENV": "production", "DB_URL": "postgres://localhost/db", "SECRET": "s3cr3t"}


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


class TestCreateAndLoad:
    def test_returns_snapshot_id(self, tmp_base):
        sid = create_snapshot("prod", SAMPLE_ENV, base=tmp_base)
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_label_in_snapshot_id(self, tmp_base):
        sid = create_snapshot("prod", SAMPLE_ENV, label="before-deploy", base=tmp_base)
        assert "before-deploy" in sid

    def test_roundtrip(self, tmp_base):
        sid = create_snapshot("prod", SAMPLE_ENV, base=tmp_base)
        loaded = load_snapshot("prod", sid, base=tmp_base)
        assert loaded == SAMPLE_ENV

    def test_load_missing_raises(self, tmp_base):
        with pytest.raises(FileNotFoundError):
            load_snapshot("prod", "nonexistent", base=tmp_base)


class TestListSnapshots:
    def test_empty_for_unknown_target(self, tmp_base):
        assert list_snapshots("ghost", base=tmp_base) == []

    def test_lists_created_snapshots(self, tmp_base):
        create_snapshot("staging", SAMPLE_ENV, label="v1", base=tmp_base)
        create_snapshot("staging", SAMPLE_ENV, label="v2", base=tmp_base)
        entries = list_snapshots("staging", base=tmp_base)
        assert len(entries) == 2

    def test_entry_fields(self, tmp_base):
        create_snapshot("staging", SAMPLE_ENV, label="check", base=tmp_base)
        entry = list_snapshots("staging", base=tmp_base)[0]
        assert "snapshot_id" in entry
        assert "created_at" in entry
        assert entry["label"] == "check"
        assert entry["keys"] == len(SAMPLE_ENV)

    def test_newest_first(self, tmp_base):
        sid1 = create_snapshot("staging", SAMPLE_ENV, label="first", base=tmp_base)
        sid2 = create_snapshot("staging", SAMPLE_ENV, label="second", base=tmp_base)
        ids = [e["snapshot_id"] for e in list_snapshots("staging", base=tmp_base)]
        assert ids.index(sid2) < ids.index(sid1)


class TestDeleteSnapshot:
    def test_delete_removes_entry(self, tmp_base):
        sid = create_snapshot("dev", SAMPLE_ENV, base=tmp_base)
        delete_snapshot("dev", sid, base=tmp_base)
        assert list_snapshots("dev", base=tmp_base) == []

    def test_delete_missing_raises(self, tmp_base):
        with pytest.raises(FileNotFoundError):
            delete_snapshot("dev", "ghost", base=tmp_base)
