"""Tests for envctl.watch and envctl.watch_render."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envctl.watch import WatchEvent, diff_snapshots, poll_target
from envctl.watch_render import render_watch_event, render_watch_summary


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

class TestDiffSnapshots:
    def test_detects_added_keys(self):
        added, _, _ = diff_snapshots({"A": "1"}, {"A": "1", "B": "2"})
        assert added == {"B": "2"}

    def test_detects_removed_keys(self):
        _, removed, _ = diff_snapshots({"A": "1", "B": "2"}, {"A": "1"})
        assert removed == {"B": "2"}

    def test_detects_changed_values(self):
        _, _, changed = diff_snapshots({"A": "old"}, {"A": "new"})
        assert changed == [("A", "old", "new")]

    def test_no_changes_returns_empty(self):
        added, removed, changed = diff_snapshots({"X": "1"}, {"X": "1"})
        assert not added and not removed and not changed

    def test_empty_snapshots_returns_empty(self):
        """Both snapshots empty should produce no diffs."""
        added, removed, changed = diff_snapshots({}, {})
        assert not added and not removed and not changed

    def test_all_keys_removed(self):
        """Transitioning from a populated snapshot to an empty one."""
        _, removed, _ = diff_snapshots({"A": "1", "B": "2"}, {})
        assert removed == {"A": "1", "B": "2"}


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------

class TestWatchEvent:
    def test_has_changes_true_when_added(self):
        e = WatchEvent(target="dev", added={"K": "v"})
        assert e.has_changes

    def test_has_changes_false_when_empty(self):
        e = WatchEvent(target="dev")
        assert not e.has_changes

    def test_summary_added(self):
        e = WatchEvent(target="dev", added={"A": "1", "B": "2"})
        assert "+2 added" in e.summary()

    def test_summary_no_changes(self):
        e = WatchEvent(target="dev")
        assert e.summary() == "no changes"

    def test_summary_combined(self):
        e = WatchEvent(
            target="dev",
            added={"A": "1"},
            removed={"B": "2"},
            changed=[("C", "x", "y")],
        )
        s = e.summary()
        assert "+1 added" in s
        assert "-1 removed" in s
        assert "~1 changed" in s

    def test_has_changes_true_when_removed(self):
        """has_changes should be True when only removals are present."""
        e = WatchEvent(target="dev", removed={"K": "v"})
        assert e.has_changes

    def test_has_changes_true_when_changed(self):
        """has_changes should be True when only changed entries are present."""
        e = WatchEvent(target="dev", changed=[("K", "old", "new")])
        assert e.has_changes


# ---------------------------------------------------------------------------
# poll_target
# ---------------------------------------------------------------------------

class TestPollTarget:
    def test_detects_change_between_polls(self):
        store = MagicMock()
        store.load.side_effect = [
            {"A": "1"},        # initial
            {"A": "1"},        # poll 1 – no change
            {"A": "2"},        # poll 2 – changed
        ]
        events = poll_target(store, "dev", interval=0, max_polls=2)
        assert len(events) == 1
        assert events[0].changed == [("A", "1", "2")]

    def test_no_events_when_stable(self):
        store = MagicMock()
        store.load.return_value = {"A": "1"}
        events = poll_target(store, "dev", interval=0, max_polls=3)
        assert events == []


# ------------------------------
