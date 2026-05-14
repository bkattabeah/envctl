"""Tests for envctl.status and envctl.status_render."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.status import TargetStatus, StatusResult, status_targets
from envctl.status_render import render_status_table, render_status_single


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("production", {"DB_HOST": "prod.db", "API_KEY": "secret", "PORT": "5432"})
    s.save("staging", {"DB_HOST": "stg.db", "PORT": "5432"})
    s.save("dev", {})
    return s


class TestTargetStatus:
    def test_health_ok(self):
        s = TargetStatus("t", 3, False, True, 0, 0)
        assert s.health == "ok"

    def test_health_warn(self):
        s = TargetStatus("t", 3, False, True, 0, 2)
        assert s.health == "warn"

    def test_health_error_lint(self):
        s = TargetStatus("t", 3, False, True, 1, 0)
        assert s.health == "error"

    def test_health_error_invalid(self):
        s = TargetStatus("t", 3, False, False, 0, 0)
        assert s.health == "error"


class TestStatusResult:
    def test_for_target_found(self):
        s = TargetStatus("prod", 5, False, True, 0, 0)
        r = StatusResult([s])
        assert r.for_target("prod") is s

    def test_for_target_missing(self):
        r = StatusResult([])
        assert r.for_target("ghost") is None

    def test_summary_all_ok(self):
        statuses = [
            TargetStatus("a", 1, False, True, 0, 0),
            TargetStatus("b", 2, False, True, 0, 0),
        ]
        r = StatusResult(statuses)
        assert "2 target(s)" in r.summary
        assert "2 ok" in r.summary

    def test_summary_mixed(self):
        statuses = [
            TargetStatus("a", 1, False, True, 0, 0),
            TargetStatus("b", 2, False, True, 0, 1),
            TargetStatus("c", 3, False, False, 1, 0),
        ]
        r = StatusResult(statuses)
        assert "1 warn" in r.summary
        assert "1 error" in r.summary


class TestStatusTargets:
    def test_returns_status_result(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        assert isinstance(result, StatusResult)

    def test_all_targets_included(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        names = {s.target for s in result.statuses}
        assert "production" in names
        assert "staging" in names
        assert "dev" in names

    def test_key_count_correct(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        prod = result.for_target("production")
        assert prod is not None
        assert prod.key_count == 3

    def test_subset_of_targets(self, store, tmp_path):
        result = status_targets(store, ["staging"], base_dir=str(tmp_path))
        assert len(result.statuses) == 1
        assert result.statuses[0].target == "staging"


class TestRenderStatusTable:
    def test_no_targets_message(self):
        out = render_status_table(StatusResult([]))
        assert "No targets" in out

    def test_header_present(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        out = render_status_table(result)
        assert "TARGET" in out
        assert "HEALTH" in out

    def test_target_names_present(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        out = render_status_table(result)
        assert "production" in out
        assert "staging" in out

    def test_summary_line_present(self, store, tmp_path):
        result = status_targets(store, base_dir=str(tmp_path))
        out = render_status_table(result)
        assert "target(s)" in out


class TestRenderStatusSingle:
    def test_contains_target_name(self):
        s = TargetStatus("myenv", 4, True, True, 0, 1, tags=["v1"])
        out = render_status_single(s)
        assert "myenv" in out

    def test_shows_frozen(self):
        s = TargetStatus("myenv", 4, True, True, 0, 0)
        out = render_status_single(s)
        assert "yes" in out

    def test_shows_tags(self):
        s = TargetStatus("myenv", 4, False, True, 0, 0, tags=["release", "stable"])
        out = render_status_single(s)
        assert "release" in out
        assert "stable" in out
