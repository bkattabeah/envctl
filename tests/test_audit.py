"""Tests for envctl.audit and envctl.audit_render."""

import os
import time
import pytest

from envctl.audit import record, load_log, clear_log, AuditEntry
from envctl.audit_render import render_audit_log


@pytest.fixture
def tmp_base(tmp_path):
    return str(tmp_path / "envctl_audit_test")


class TestRecord:
    def test_returns_audit_entry(self, tmp_base):
        entry = record(tmp_base, "set", "production", ["DB_URL", "API_KEY"])
        assert isinstance(entry, AuditEntry)
        assert entry.action == "set"
        assert entry.target == "production"
        assert "API_KEY" in entry.keys

    def test_keys_are_sorted(self, tmp_base):
        entry = record(tmp_base, "set", "staging", ["Z_KEY", "A_KEY"])
        assert entry.keys == ["A_KEY", "Z_KEY"]

    def test_label_stored(self, tmp_base):
        entry = record(tmp_base, "snapshot", "dev", ["FOO"], label="before-deploy")
        assert entry.label == "before-deploy"

    def test_log_file_created(self, tmp_base):
        record(tmp_base, "delete", "dev", ["OLD_KEY"])
        assert os.path.exists(os.path.join(tmp_base, "audit.log"))


class TestLoadLog:
    def test_empty_when_no_file(self, tmp_base):
        entries = load_log(tmp_base)
        assert entries == []

    def test_loads_recorded_entries(self, tmp_base):
        record(tmp_base, "set", "prod", ["X"])
        record(tmp_base, "import", "prod", ["Y", "Z"])
        entries = load_log(tmp_base)
        assert len(entries) == 2

    def test_filter_by_target(self, tmp_base):
        record(tmp_base, "set", "prod", ["A"])
        record(tmp_base, "set", "staging", ["B"])
        prod_entries = load_log(tmp_base, target="prod")
        assert all(e.target == "prod" for e in prod_entries)
        assert len(prod_entries) == 1

    def test_roundtrip_preserves_fields(self, tmp_base):
        before = time.time()
        record(tmp_base, "delete", "dev", ["SECRET"], label="cleanup")
        entries = load_log(tmp_base)
        e = entries[0]
        assert e.action == "delete"
        assert e.target == "dev"
        assert e.keys == ["SECRET"]
        assert e.label == "cleanup"
        assert e.timestamp >= before


class TestClearLog:
    def test_removes_log_file(self, tmp_base):
        record(tmp_base, "set", "prod", ["K"])
        clear_log(tmp_base)
        assert not os.path.exists(os.path.join(tmp_base, "audit.log"))

    def test_no_error_if_no_file(self, tmp_base):
        clear_log(tmp_base)  # should not raise


class TestRenderAuditLog:
    def test_empty_message(self):
        output = render_audit_log([])
        assert "No audit entries" in output

    def test_header_present(self, tmp_base):
        record(tmp_base, "set", "prod", ["FOO"])
        entries = load_log(tmp_base)
        output = render_audit_log(entries, use_color=False)
        assert "TIMESTAMP" in output
        assert "ACTION" in output
        assert "TARGET" in output

    def test_entry_appears_in_output(self, tmp_base):
        record(tmp_base, "import", "staging", ["DB_HOST"])
        entries = load_log(tmp_base)
        output = render_audit_log(entries, use_color=False)
        assert "staging" in output
        assert "import" in output
        assert "DB_HOST" in output

    def test_label_shown_in_output(self, tmp_base):
        record(tmp_base, "snapshot", "prod", ["A"], label="v1.2")
        entries = load_log(tmp_base)
        output = render_audit_log(entries, use_color=False)
        assert "v1.2" in output
