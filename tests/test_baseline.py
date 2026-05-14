"""Tests for envctl.baseline and envctl.baseline_render."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.baseline import (
    BaselineResult,
    set_baseline,
    load_baseline,
    list_baselines,
    delete_baseline,
)
from envctl.baseline_render import (
    render_baseline_saved,
    render_baseline_list,
    render_baseline_deleted,
    render_baseline_not_found,
)


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_path=tmp_path)
    s.save("prod", {"DB_HOST": "db.prod", "API_KEY": "secret"})
    s.save("staging", {"DB_HOST": "db.staging"})
    return s


class TestSetBaseline:
    def test_returns_baseline_result(self, store):
        result = set_baseline(store, "prod")
        assert isinstance(result, BaselineResult)

    def test_baseline_id_contains_target(self, store):
        result = set_baseline(store, "prod")
        assert "prod" in result.baseline_id

    def test_label_in_baseline_id(self, store):
        result = set_baseline(store, "prod", label="before-deploy")
        assert "before-deploy" in result.baseline_id

    def test_env_matches_target(self, store):
        result = set_baseline(store, "prod")
        assert result.env == {"DB_HOST": "db.prod", "API_KEY": "secret"}

    def test_label_stored(self, store):
        result = set_baseline(store, "prod", label="v1")
        assert result.label == "v1"

    def test_file_created_on_disk(self, store, tmp_path):
        result = set_baseline(store, "prod")
        path = tmp_path / ".envctl" / "baselines" / f"{result.baseline_id}.json"
        assert path.exists()


class TestLoadBaseline:
    def test_roundtrip(self, store):
        saved = set_baseline(store, "prod", label="snap")
        loaded = load_baseline(store.base_path, saved.baseline_id)
        assert loaded.env == saved.env
        assert loaded.label == "snap"
        assert loaded.target == "prod"

    def test_missing_raises(self, store):
        with pytest.raises(FileNotFoundError):
            load_baseline(store.base_path, "nonexistent__baseline__0")


class TestListBaselines:
    def test_returns_all_baselines(self, store):
        set_baseline(store, "prod")
        set_baseline(store, "staging")
        results = list_baselines(store.base_path)
        assert len(results) == 2

    def test_filter_by_target(self, store):
        set_baseline(store, "prod")
        set_baseline(store, "staging")
        results = list_baselines(store.base_path, target="prod")
        assert all(r.target == "prod" for r in results)
        assert len(results) == 1

    def test_empty_when_no_baselines(self, tmp_path):
        assert list_baselines(tmp_path) == []


class TestDeleteBaseline:
    def test_returns_true_when_deleted(self, store):
        result = set_baseline(store, "prod")
        assert delete_baseline(store.base_path, result.baseline_id) is True

    def test_returns_false_when_missing(self, store):
        assert delete_baseline(store.base_path, "ghost__baseline__0") is False

    def test_file_removed(self, store, tmp_path):
        result = set_baseline(store, "prod")
        delete_baseline(store.base_path, result.baseline_id)
        path = tmp_path / ".envctl" / "baselines" / f"{result.baseline_id}.json"
        assert not path.exists()


class TestBaselineRender:
    def test_saved_contains_id(self, store):
        result = set_baseline(store, "prod", label="go")
        out = render_baseline_saved(result)
        assert result.baseline_id in out

    def test_list_no_baselines_message(self, store):
        out = render_baseline_list([])
        assert "No baselines" in out

    def test_list_shows_ids(self, store):
        r1 = set_baseline(store, "prod")
        r2 = set_baseline(store, "staging")
        out = render_baseline_list([r1, r2])
        assert r1.baseline_id in out
        assert r2.baseline_id in out

    def test_deleted_found(self, store):
        out = render_baseline_deleted("some-id", found=True)
        assert "deleted" in out.lower()

    def test_deleted_not_found(self, store):
        out = render_baseline_deleted("some-id", found=False)
        assert "not found" in out.lower()

    def test_not_found_render(self, store):
        out = render_baseline_not_found("missing-id")
        assert "missing-id" in out
