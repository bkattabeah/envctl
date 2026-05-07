"""Tests for envctl.pin — pin key/value enforcement for targets."""

import pytest

from envctl.pin import (
    add_pin,
    check_pins,
    load_pins,
    remove_pin,
    save_pins,
    PinCheckResult,
    PinViolation,
)


@pytest.fixture
def tmp_base(tmp_path):
    return str(tmp_path)


class TestSaveAndLoad:
    def test_roundtrip(self, tmp_base):
        save_pins(tmp_base, "prod", {"LOG_LEVEL": "error", "DEBUG": "false"})
        result = load_pins(tmp_base, "prod")
        assert result == {"LOG_LEVEL": "error", "DEBUG": "false"}

    def test_missing_target_returns_empty(self, tmp_base):
        assert load_pins(tmp_base, "nonexistent") == {}

    def test_creates_directory(self, tmp_base):
        save_pins(tmp_base, "staging", {"KEY": "val"})
        pins = load_pins(tmp_base, "staging")
        assert pins["KEY"] == "val"


class TestAddRemovePin:
    def test_add_pin(self, tmp_base):
        add_pin(tmp_base, "prod", "DEBUG", "false")
        assert load_pins(tmp_base, "prod")["DEBUG"] == "false"

    def test_add_multiple_pins(self, tmp_base):
        add_pin(tmp_base, "prod", "A", "1")
        add_pin(tmp_base, "prod", "B", "2")
        pins = load_pins(tmp_base, "prod")
        assert pins == {"A": "1", "B": "2"}

    def test_remove_existing_pin(self, tmp_base):
        add_pin(tmp_base, "prod", "DEBUG", "false")
        removed = remove_pin(tmp_base, "prod", "DEBUG")
        assert removed is True
        assert "DEBUG" not in load_pins(tmp_base, "prod")

    def test_remove_nonexistent_pin_returns_false(self, tmp_base):
        result = remove_pin(tmp_base, "prod", "MISSING_KEY")
        assert result is False

    def test_overwrite_pin(self, tmp_base):
        add_pin(tmp_base, "prod", "LOG_LEVEL", "info")
        add_pin(tmp_base, "prod", "LOG_LEVEL", "error")
        assert load_pins(tmp_base, "prod")["LOG_LEVEL"] == "error"


class TestCheckPins:
    def test_passes_when_all_satisfied(self, tmp_base):
        add_pin(tmp_base, "prod", "DEBUG", "false")
        result = check_pins(tmp_base, "prod", {"DEBUG": "false", "OTHER": "x"})
        assert result.passed is True
        assert result.violations == []

    def test_detects_wrong_value(self, tmp_base):
        add_pin(tmp_base, "prod", "DEBUG", "false")
        result = check_pins(tmp_base, "prod", {"DEBUG": "true"})
        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0].key == "DEBUG"
        assert result.violations[0].expected == "false"
        assert result.violations[0].actual == "true"

    def test_detects_missing_key(self, tmp_base):
        add_pin(tmp_base, "prod", "REQUIRED", "yes")
        result = check_pins(tmp_base, "prod", {})
        assert result.passed is False
        assert result.violations[0].actual is None

    def test_no_pins_always_passes(self, tmp_base):
        result = check_pins(tmp_base, "prod", {"ANY": "value"})
        assert result.passed is True

    def test_summary_passed(self, tmp_base):
        result = PinCheckResult(target="prod", violations=[])
        assert "All pins satisfied" in result.summary()

    def test_summary_with_violations(self, tmp_base):
        v = PinViolation(key="DEBUG", expected="false", actual="true")
        result = PinCheckResult(target="prod", violations=[v])
        summary = result.summary()
        assert "1 pin violation" in summary
        assert "DEBUG" in summary

    def test_violation_str_missing(self):
        v = PinViolation(key="K", expected="v", actual=None)
        assert "<missing>" in str(v)
