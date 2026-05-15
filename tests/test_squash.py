"""Tests for envctl.squash."""
import pytest

from envctl.env_store import EnvStore
from envctl.squash import squash_targets, SquashResult


@pytest.fixture
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


class TestSquashTargets:
    def test_returns_squash_result(self, store):
        store.save("a", {"X": "1"})
        result = squash_targets(store, ["a"], "out")
        assert isinstance(result, SquashResult)

    def test_all_keys_present(self, store):
        store.save("a", {"X": "1", "Y": "2"})
        store.save("b", {"Z": "3"})
        result = squash_targets(store, ["a", "b"], "out")
        assert result.env == {"X": "1", "Y": "2", "Z": "3"}

    def test_last_strategy_overwrites(self, store):
        store.save("a", {"X": "from_a"})
        store.save("b", {"X": "from_b"})
        result = squash_targets(store, ["a", "b"], "out", strategy="last")
        assert result.env["X"] == "from_b"
        assert "X" in result.overwritten_keys

    def test_first_strategy_keeps_first(self, store):
        store.save("a", {"X": "from_a"})
        store.save("b", {"X": "from_b"})
        result = squash_targets(store, ["a", "b"], "out", strategy="first")
        assert result.env["X"] == "from_a"
        assert result.overwritten_keys == []

    def test_skips_missing_source(self, store):
        store.save("a", {"X": "1"})
        result = squash_targets(store, ["a", "ghost"], "out")
        assert "ghost" in result.skipped_sources
        assert "a" in result.sources

    def test_key_filter_applied(self, store):
        store.save("a", {"X": "1", "Y": "2", "Z": "3"})
        result = squash_targets(store, ["a"], "out", keys=["X", "Z"])
        assert "Y" not in result.env
        assert result.env == {"X": "1", "Z": "3"}

    def test_destination_saved_to_store(self, store):
        store.save("a", {"K": "v"})
        squash_targets(store, ["a"], "dest")
        loaded = store.load("dest")
        assert loaded["K"] == "v"

    def test_save_false_does_not_persist(self, store):
        store.save("a", {"K": "v"})
        squash_targets(store, ["a"], "dest", save=False)
        with pytest.raises(FileNotFoundError):
            store.load("dest")

    def test_invalid_strategy_raises(self, store):
        store.save("a", {"K": "v"})
        with pytest.raises(ValueError, match="strategy"):
            squash_targets(store, ["a"], "out", strategy="random")

    def test_empty_sources_list(self, store):
        result = squash_targets(store, [], "out")
        assert result.env == {}
        assert result.sources == []

    def test_destination_name_in_result(self, store):
        store.save("a", {"K": "v"})
        result = squash_targets(store, ["a"], "my-dest")
        assert result.destination == "my-dest"

    def test_summary_contains_destination(self, store):
        store.save("a", {"K": "v"})
        result = squash_targets(store, ["a"], "prod")
        assert "prod" in result.summary()

    def test_summary_lists_skipped(self, store):
        store.save("a", {"K": "v"})
        result = squash_targets(store, ["a", "missing"], "out")
        assert "missing" in result.summary()
