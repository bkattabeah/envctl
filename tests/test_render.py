"""Tests for envctl.render module."""

from envctl.render import render_diff_table, render_env_table, colorize, ANSI_GREEN, ANSI_RED


class TestColorize:
    def test_contains_text(self):
        result = colorize("hello", ANSI_GREEN)
        assert "hello" in result

    def test_contains_reset(self):
        result = colorize("hello", ANSI_GREEN)
        assert "\033[0m" in result

    def test_bold_flag(self):
        result = colorize("hello", ANSI_GREEN, bold=True)
        assert "\033[1m" in result


class TestRenderDiffTable:
    def test_added_keys_present(self):
        output = render_diff_table(added={"NEW_KEY": "val"}, removed={}, changed={})
        assert "NEW_KEY" in output
        assert "Added" in output

    def test_removed_keys_present(self):
        output = render_diff_table(added={}, removed={"OLD_KEY": "val"}, changed={})
        assert "OLD_KEY" in output
        assert "Removed" in output

    def test_changed_shows_before_after(self):
        output = render_diff_table(added={}, removed={}, changed={"X": ("old", "new")})
        assert "before" in output
        assert "after" in output
        assert "old" in output
        assert "new" in output

    def test_mask_hides_values(self):
        output = render_diff_table(
            added={"SECRET": "supersecret"}, removed={}, changed={}, mask_secrets=True
        )
        assert "supersecret" not in output
        assert "***" in output

    def test_no_differences_message(self):
        output = render_diff_table(added={}, removed={}, changed={})
        assert "No differences" in output

    def test_ends_with_newline(self):
        output = render_diff_table(added={"A": "1"}, removed={}, changed={})
        assert output.endswith("\n")


class TestRenderEnvTable:
    def test_shows_key_value(self):
        output = render_env_table({"FOO": "bar"})
        assert "FOO=bar" in output

    def test_empty_env(self):
        output = render_env_table({})
        assert "empty" in output

    def test_title_shown(self):
        output = render_env_table({"A": "1"}, title="production")
        assert "production" in output

    def test_sorted_output(self):
        output = render_env_table({"Z": "1", "A": "2"})
        assert output.index("A=") < output.index("Z=")
