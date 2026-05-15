"""Tests for envctl.pipeline."""
from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.pipeline import PipelineResult, PipelineStep, run_pipeline


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


def _upper_step() -> PipelineStep:
    return PipelineStep(name="upper", fn=lambda env: {k: v.upper() for k, v in env.items()})


def _add_key_step(key: str, value: str) -> PipelineStep:
    def _fn(env):
        env[key] = value
        return env
    return PipelineStep(name=f"add_{key}", fn=_fn)


def _remove_key_step(key: str) -> PipelineStep:
    def _fn(env):
        env.pop(key, None)
        return env
    return PipelineStep(name=f"remove_{key}", fn=_fn)


def _bad_step() -> PipelineStep:
    def _fn(env):
        raise RuntimeError("intentional failure")
    return PipelineStep(name="bad_step", fn=_fn)


class TestRunPipeline:
    def test_returns_pipeline_result(self, store):
        store.save("prod", {"A": "one"})
        result = run_pipeline(store, "prod", [])
        assert isinstance(result, PipelineResult)

    def test_missing_target_returns_error(self, store):
        result = run_pipeline(store, "missing", [])
        assert result.error is not None
        assert "missing" in result.error

    def test_single_step_applied(self, store):
        store.save("dev", {"KEY": "hello"})
        result = run_pipeline(store, "dev", [_upper_step()])
        assert result.final_env["KEY"] == "HELLO"
        assert "upper" in result.steps_applied

    def test_multiple_steps_applied_in_order(self, store):
        store.save("dev", {"X": "val"})
        steps = [_upper_step(), _add_key_step("NEW", "added")]
        result = run_pipeline(store, "dev", steps)
        assert result.final_env["X"] == "VAL"
        assert result.final_env["NEW"] == "added"
        assert result.steps_applied == ["upper", "add_NEW"]

    def test_failing_step_is_skipped(self, store):
        store.save("dev", {"A": "x"})
        result = run_pipeline(store, "dev", [_bad_step(), _upper_step()])
        assert "bad_step" in result.skipped
        assert "upper" in result.steps_applied

    def test_remove_key_step(self, store):
        store.save("dev", {"A": "1", "B": "2"})
        result = run_pipeline(store, "dev", [_remove_key_step("A")])
        assert "A" not in result.final_env
        assert "B" in result.final_env

    def test_dry_run_does_not_persist(self, store):
        store.save("dev", {"KEY": "original"})
        run_pipeline(store, "dev", [_upper_step()], dry_run=True)
        assert store.load("dev")["KEY"] == "original"

    def test_non_dry_run_persists(self, store):
        store.save("dev", {"KEY": "original"})
        run_pipeline(store, "dev", [_upper_step()], dry_run=False)
        assert store.load("dev")["KEY"] == "ORIGINAL"

    def test_initial_env_preserved_in_result(self, store):
        store.save("dev", {"KEY": "before"})
        result = run_pipeline(store, "dev", [_upper_step()])
        assert result.initial_env["KEY"] == "before"

    def test_summary_no_error(self, store):
        store.save("dev", {"K": "v"})
        result = run_pipeline(store, "dev", [_upper_step()])
        s = result.summary()
        assert "dev" in s
        assert "step" in s

    def test_summary_with_error(self, store):
        result = run_pipeline(store, "ghost", [])
        s = result.summary()
        assert "failed" in s.lower() or "error" in s.lower()
