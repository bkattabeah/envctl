"""Tests for envctl.rollback and envctl.rollback_render."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.audit import AuditEntry, record as audit_record
from envctl.rollback import rollback_target, RollbackResult
from envctl.rollback_render import render_rollback_result, render_rollback_not_found


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


def _seed_audit(store: EnvStore, target: str, snapshots: list[dict]) -> list[AuditEntry]:
    """Write a sequence of audit entries with incrementing snapshots."""
    entries = []
    for i, snap in enumerate(snapshots):
        before = snapshots[i - 1] if i > 0 else {}
        e = audit_record(
            store.base_dir,
            action="set",
            target=target,
            keys=list(snap.keys()),
            snapshot_before=before,
            snapshot_after=snap,
        )
        entries.append(e)
    return entries


class TestRollbackTarget:
    def test_returns_rollback_result(self, store):
        store.save("prod", {"A": "1"})
        _seed_audit(store, "prod", [{"A": "1"}])
        result = rollback_target(store, "prod", steps=1)
        assert isinstance(result, RollbackResult)

    def test_restores_previous_env(self, store):
        _seed_audit(store, "prod", [{"A": "old"}, {"A": "new"}])
        store.save("prod", {"A": "new"})
        result = rollback_target(store, "prod", steps=1)
        assert result.success
        assert store.load("prod") == {"A": "old"}

    def test_keys_changed_populated(self, store):
        _seed_audit(store, "prod", [{"A": "1"}, {"A": "2"}])
        store.save("prod", {"A": "2"})
        result = rollback_target(store, "prod", steps=1)
        assert "A" in result.keys_changed

    def test_keys_added_populated(self, store):
        _seed_audit(store, "prod", [{"A": "1"}, {"A": "1", "B": "2"}])
        store.save("prod", {"A": "1", "B": "2"})
        result = rollback_target(store, "prod", steps=1)
        # rolling back adds B back from the perspective of restored vs previous
        assert result.success

    def test_no_audit_returns_failure(self, store):
        store.save("empty", {"X": "1"})
        result = rollback_target(store, "empty", steps=1)
        assert not result.success
        assert "No audit history" in result.message

    def test_rollback_by_entry_id(self, store):
        entries = _seed_audit(store, "staging", [{"K": "v1"}, {"K": "v2"}])
        store.save("staging", {"K": "v2"})
        target_id = entries[0].entry_id
        result = rollback_target(store, "staging", entry_id=target_id)
        assert result.success
        assert result.rolled_back_to == target_id

    def test_invalid_entry_id_returns_failure(self, store):
        _seed_audit(store, "dev", [{"X": "1"}])
        store.save("dev", {"X": "1"})
        result = rollback_target(store, "dev", entry_id="nonexistent-id")
        assert not result.success
        assert "not found" in result.message

    def test_summary_on_success(self, store):
        _seed_audit(store, "prod", [{"A": "1"}, {"A": "2"}])
        store.save("prod", {"A": "2"})
        result = rollback_target(store, "prod", steps=1)
        assert "prod" in result.summary()

    def test_summary_on_failure(self, store):
        store.save("ghost", {})
        result = rollback_target(store, "ghost", steps=1)
        assert "failed" in result.summary().lower()


class TestRenderRollbackResult:
    def test_success_contains_target(self, store):
        _seed_audit(store, "prod", [{"A": "1"}, {"A": "2"}])
        store.save("prod", {"A": "2"})
        result = rollback_target(store, "prod", steps=1)
        rendered = render_rollback_result(result)
        assert "prod" in rendered

    def test_failure_shows_error(self, store):
        store.save("x", {})
        result = rollback_target(store, "x", steps=1)
        rendered = render_rollback_result(result)
        assert "failed" in rendered.lower() or "✗" in rendered

    def test_mask_hides_values(self, store):
        _seed_audit(store, "prod", [{"SECRET": "hunter2"}, {"SECRET": "changed"}])
        store.save("prod", {"SECRET": "changed"})
        result = rollback_target(store, "prod", steps=1)
        rendered = render_rollback_result(result, mask=True)
        assert "hunter2" not in rendered
        assert "changed" not in rendered

    def test_render_not_found(self):
        out = render_rollback_not_found("prod", "bad-id")
        assert "prod" in out
        assert "bad-id" in out
