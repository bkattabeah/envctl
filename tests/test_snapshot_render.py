"""Tests for envctl.snapshot_render."""

from envctl.snapshot_render import render_snapshot_diff, render_snapshot_list

SAMPLE_ENTRIES = [
    {
        "snapshot_id": "20240601T120000Z_before-deploy",
        "label": "before-deploy",
        "created_at": "2024-06-01T12:00:00+00:00",
        "keys": 5,
    },
    {
        "snapshot_id": "20240531T090000Z",
        "label": None,
        "created_at": "2024-05-31T09:00:00+00:00",
        "keys": 4,
    },
]


class TestRenderSnapshotList:
    def test_no_snapshots_message(self):
        out = render_snapshot_list("prod", [], color=False)
        assert "No snapshots" in out
        assert "prod" in out

    def test_header_present(self):
        out = render_snapshot_list("prod", SAMPLE_ENTRIES, color=False)
        assert "SNAPSHOT ID" in out
        assert "LABEL" in out
        assert "CREATED AT" in out
        assert "KEYS" in out

    def test_entry_ids_present(self):
        out = render_snapshot_list("prod", SAMPLE_ENTRIES, color=False)
        assert "20240601T120000Z_before-deploy" in out
        assert "20240531T090000Z" in out

    def test_label_shown(self):
        out = render_snapshot_list("prod", SAMPLE_ENTRIES, color=False)
        assert "before-deploy" in out

    def test_key_count_shown(self):
        out = render_snapshot_list("prod", SAMPLE_ENTRIES, color=False)
        assert "5" in out
        assert "4" in out

    def test_color_output_contains_text(self):
        out = render_snapshot_list("prod", SAMPLE_ENTRIES, color=True)
        assert "SNAPSHOT ID" in out

    def test_no_snapshots_color(self):
        out = render_snapshot_list("prod", [], color=True)
        assert "No snapshots" in out


class TestRenderSnapshotDiff:
    def test_no_diff_message(self):
        env = {"KEY": "value"}
        out = render_snapshot_diff("prod", "snap1", env, env, color=False)
        assert "No differences" in out
        assert "snap1" in out
        assert "prod" in out

    def test_diff_shows_changed_key(self):
        snap_env = {"KEY": "old", "STABLE": "same"}
        curr_env = {"KEY": "new", "STABLE": "same"}
        out = render_snapshot_diff("prod", "snap1", snap_env, curr_env, color=False)
        assert "KEY" in out

    def test_diff_shows_added_key(self):
        snap_env = {"A": "1"}
        curr_env = {"A": "1", "B": "2"}
        out = render_snapshot_diff("prod", "snap1", snap_env, curr_env, color=False)
        assert "B" in out

    def test_mask_keys_applied(self):
        snap_env = {"SECRET": "old_secret"}
        curr_env = {"SECRET": "new_secret"}
        out = render_snapshot_diff(
            "prod", "snap1", snap_env, curr_env, mask_keys=["SECRET"], color=False
        )
        assert "old_secret" not in out
        assert "new_secret" not in out
        assert "SECRET" in out
