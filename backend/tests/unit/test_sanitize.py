"""
Unit tests for input sanitization (backend/app/core/sanitize.py).

Pure functions — no external services required.
"""

from backend.app.core.sanitize import (
    sanitize_html,
    sanitize_text,
    sanitize_url,
    sanitize_list,
    SanitizationMiddleware,
)


class TestSanitizeHtml:
    def test_empty_returns_empty(self):
        assert sanitize_html("") == ""

    def test_strips_script_tags(self):
        out = sanitize_html("<script>alert('xss')</script>hello", strip_tags=True)
        assert "<script>" not in out
        assert "hello" in out

    def test_keeps_allowed_tags(self):
        out = sanitize_html("<strong>bold</strong>")
        assert "<strong>" in out

    def test_removes_disallowed_tags_but_keeps_text(self):
        out = sanitize_html("<div><strong>keep</strong></div>")
        assert "<div>" not in out
        assert "keep" in out


class TestSanitizeText:
    def test_empty(self):
        assert sanitize_text("") == ""

    def test_strips_all_html(self):
        out = sanitize_text("<b>hi</b> <i>there</i>")
        assert "<b>" not in out and "<i>" not in out
        assert "hi" in out and "there" in out


class TestSanitizeUrl:
    def test_none_for_empty(self):
        assert sanitize_url("") is None

    def test_valid_https(self):
        assert sanitize_url("https://example.com") == "https://example.com"

    def test_valid_mailto(self):
        assert sanitize_url("mailto:test@example.com") == "mailto:test@example.com"

    def test_rejects_javascript_scheme(self):
        assert sanitize_url("javascript:alert(1)") is None

    def test_rejects_relative(self):
        assert sanitize_url("/some/path") is None


class TestSanitizeList:
    def test_empty(self):
        assert sanitize_list([]) == []

    def test_filters_and_sanitizes(self):
        out = sanitize_list(["<script>x</script>ok", "", "plain"])
        assert "plain" in out
        assert all("<script>" not in item for item in out)
        # falsy entries are dropped
        assert "" not in out


class TestSanitizeDict:
    def test_sanitizes_named_string_field(self):
        data = {"bio": "<script>x</script>hi", "name": "<b>keep</b>"}
        out = SanitizationMiddleware.sanitize_dict(data, ["bio"], strip_tags=True)
        assert "<script>" not in out["bio"]
        # untouched field is unchanged
        assert out["name"] == "<b>keep</b>"

    def test_sanitizes_list_field(self):
        data = {"tags": ["<i>a</i>", "b"]}
        out = SanitizationMiddleware.sanitize_dict(data, ["tags"], strip_tags=True)
        assert all("<i>" not in t for t in out["tags"])

    def test_ignores_missing_fields(self):
        data = {"a": "x"}
        out = SanitizationMiddleware.sanitize_dict(data, ["nonexistent"])
        assert out == {"a": "x"}
