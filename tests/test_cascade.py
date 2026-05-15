"""Tests for envctl.cascade."""

import pytest
from envctl.env_store import EnvStore
from envctl.cascade import cascade_target, CascadeResult


@pytest.fixture
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


class TestCascadeTarget:
    def test_returns_cascade_result(self, store):
        store.save("base", {"A": "1"})
        store.save("dev", {})
        result = cascade_target(store, "base", ["dev"])
        assert isinstance(result, CascadeResult)

    def test_copies_all_keys_by_default(self, store):
        store.save("base", {"A": "1", "B": "2"})
        store.save("dev", {})
        cascade_target(store, "base", ["dev"])
        assert store.load("dev") == {"A": "1", "B": "2"}

    def test_copies_only_specified_keys(self, store):
        store.save("base", {"A": "1", "B": "2", "C": "3"})
        store.save("dev", {})
        cascade_target(store, "base", ["dev"], keys=["A", "C"])
        dev = store.load("dev")
        assert dev["A"] == "1"
        assert dev["C"] == "3"
        assert "B" not in dev

    def test_skips_existing_key_without_overwrite(self, store):
        store.save("base", {"A": "new"})
        store.save("dev", {"A": "old"})
        result = cascade_target(store, "base", ["dev"], overwrite=False)
        assert store.load("dev")["A"] == "old"
        assert "dev" in result.skipped.get("A", [])

    def test_overwrites_existing_key_when_flag_set(self, store):
        store.save("base", {"A": "new"})
        store.save("dev", {"A": "old"})
        cascade_target(store, "base", ["dev"], overwrite=True)
        assert store.load("dev")["A"] == "new"

    def test_applied_tracks_updated_targets(self, store):
        store.save("base", {"X": "1"})
        store.save("dev", {})
        store.save("staging", {})
        result = cascade_target(store, "base", ["dev", "staging"])
        assert set(result.applied["X"]) == {"dev", "staging"}

    def test_missing_target_recorded(self, store):
        store.save("base", {"A": "1"})
        result = cascade_target(store, "base", ["ghost"])
        assert "ghost" in result.missing_targets

    def test_missing_target_not_created(self, store):
        store.save("base", {"A": "1"})
        cascade_target(store, "base", ["ghost"])
        assert "ghost" not in store.list_targets()

    def test_ignores_keys_absent_in_source(self, store):
        store.save("base", {"A": "1"})
        store.save("dev", {})
        result = cascade_target(store, "base", ["dev"], keys=["A", "MISSING"])
        assert "MISSING" not in store.load("dev")
        assert "MISSING" not in result.applied

    def test_summary_contains_source(self, store):
        store.save("base", {"A": "1"})
        store.save("dev", {})
        result = cascade_target(store, "base", ["dev"])
        assert "base" in result.summary()

    def test_summary_mentions_missing_targets(self, store):
        store.save("base", {"A": "1"})
        result = cascade_target(store, "base", ["nowhere"])
        assert "nowhere" in result.summary()

    def test_multiple_targets_each_updated(self, store):
        store.save("base", {"DB": "prod"})
        for t in ["dev", "staging", "qa"]:
            store.save(t, {})
        cascade_target(store, "base", ["dev", "staging", "qa"])
        for t in ["dev", "staging", "qa"]:
            assert store.load(t)["DB"] == "prod"
