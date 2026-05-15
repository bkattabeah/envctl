"""Tests for envctl.score."""

import pytest

from envctl.env_store import EnvStore
from envctl.score import ScoreResult, score_target, _count_duplicate_prefixes


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


# ---------------------------------------------------------------------------
# Unit tests for ScoreResult helpers
# ---------------------------------------------------------------------------

class TestScoreResult:
    def _make(self, **kwargs):
        defaults = dict(
            target="prod",
            total_keys=5,
            lint_errors=0,
            lint_warnings=0,
            validation_errors=0,
            validation_warnings=0,
            missing_values=0,
            duplicate_prefixes=0,
        )
        defaults.update(kwargs)
        return ScoreResult(**defaults)

    def test_perfect_score(self):
        r = self._make()
        assert r.score == 100

    def test_grade_a(self):
        assert self._make().grade == "A"

    def test_grade_b(self):
        r = self._make(lint_warnings=5)  # -15
        assert r.grade == "B"

    def test_grade_f(self):
        r = self._make(lint_errors=10)  # -100
        assert r.score == 0
        assert r.grade == "F"

    def test_score_never_below_zero(self):
        r = self._make(lint_errors=20, validation_errors=20)
        assert r.score == 0

    def test_summary_contains_target(self):
        r = self._make()
        assert "prod" in r.summary()

    def test_summary_contains_score(self):
        r = self._make()
        assert "score=100" in r.summary()

    def test_summary_contains_grade(self):
        r = self._make()
        assert "grade=A" in r.summary()


# ---------------------------------------------------------------------------
# _count_duplicate_prefixes
# ---------------------------------------------------------------------------

def test_no_duplicates():
    env = {"APP_HOST": "x", "DB_HOST": "y", "CACHE_TTL": "30"}
    assert _count_duplicate_prefixes(env) == 0


def test_duplicate_prefix_counted():
    env = {"APP_HOST": "x", "APP_PORT": "80", "DB_HOST": "y"}
    # APP appears twice -> 2 keys contribute to the duplicate count
    assert _count_duplicate_prefixes(env) == 2


def test_keys_without_underscore_ignored():
    env = {"HOST": "x", "PORT": "80"}
    assert _count_duplicate_prefixes(env) == 0


# ---------------------------------------------------------------------------
# Integration: score_target
# ---------------------------------------------------------------------------

class TestScoreTarget:
    def test_returns_score_result(self, store):
        store.save("staging", {"APP_HOST": "localhost", "APP_PORT": "8080"})
        result = score_target(store, "staging")
        assert isinstance(result, ScoreResult)

    def test_total_keys_correct(self, store):
        store.save("staging", {"A": "1", "B": "2", "C": "3"})
        result = score_target(store, "staging")
        assert result.total_keys == 3

    def test_empty_value_counted(self, store):
        store.save("staging", {"KEY": "", "OTHER": "val"})
        result = score_target(store, "staging")
        assert result.missing_values == 1

    def test_clean_env_scores_high(self, store):
        store.save("prod", {"APP_HOST": "example.com", "APP_PORT": "443"})
        result = score_target(store, "prod")
        assert result.score >= 70

    def test_breakdown_keys_present(self, store):
        store.save("dev", {"X": "1"})
        result = score_target(store, "dev")
        assert "lint_errors" in result.breakdown
        assert "missing_values" in result.breakdown
