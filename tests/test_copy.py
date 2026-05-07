"""Tests for envctl.copy (copy_keys) and envctl.copy_render."""

import pytest

from envctl.env_store import EnvStore
from envctl.copy import copy_keys, CopyResult
from envctl.copy_render import render_copy_result


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("src", {"A": "1", "B": "2", "C": "3"})
    s.save("dst", {"B": "existing", "D": "4"})
    return s


class TestCopyKeys:
    def test_copies_requested_keys(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        assert "A" in store.load("dst")
        assert store.load("dst")["A"] == "1"

    def test_copied_keys_in_result(self, store):
        result = copy_keys(store, "src", "dst", ["A", "C"])
        assert set(result.copied.keys()) == {"A", "C"}

    def test_skips_existing_key_without_overwrite(self, store):
        result = copy_keys(store, "src", "dst", ["B"])
        assert "B" in result.skipped
        assert store.load("dst")["B"] == "existing"

    def test_overwrites_when_flag_set(self, store):
        result = copy_keys(store, "src", "dst", ["B"], overwrite=True)
        assert "B" in result.copied
        assert store.load("dst")["B"] == "2"

    def test_records_missing_keys(self, store):
        result = copy_keys(store, "src", "dst", ["NOPE"])
        assert "NOPE" in result.missing
        assert not result.copied

    def test_rename_applies_new_key_name(self, store):
        result = copy_keys(store, "src", "dst", ["A"], rename={"A": "A_RENAMED"})
        dst = store.load("dst")
        assert "A_RENAMED" in dst
        assert "A" not in dst
        assert "A_RENAMED" in result.copied

    def test_does_not_save_when_nothing_copied(self, store):
        before = store.load("dst").copy()
        copy_keys(store, "src", "dst", ["B"])  # skipped
        assert store.load("dst") == before

    def test_summary_all_copied(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        assert "copied" in result.summary()

    def test_summary_mixed(self, store):
        result = copy_keys(store, "src", "dst", ["A", "B", "NOPE"])
        summary = result.summary()
        assert "copied" in summary
        assert "skipped" in summary
        assert "not found" in summary


class TestRenderCopyResult:
    def test_contains_source_and_dest(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        out = render_copy_result(result)
        assert "src" in out
        assert "dst" in out

    def test_masks_values_by_default(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        out = render_copy_result(result)
        assert "***" in out
        assert "1" not in out

    def test_shows_values_when_mask_false(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        out = render_copy_result(result, mask=False)
        assert "1" in out

    def test_shows_skipped_section(self, store):
        result = copy_keys(store, "src", "dst", ["B"])
        out = render_copy_result(result)
        assert "Skipped" in out

    def test_shows_missing_section(self, store):
        result = copy_keys(store, "src", "dst", ["NOPE"])
        out = render_copy_result(result)
        assert "Not found" in out

    def test_shows_summary_line(self, store):
        result = copy_keys(store, "src", "dst", ["A"])
        out = render_copy_result(result)
        assert "Summary" in out
