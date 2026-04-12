"""Unit tests for helper utilities."""

from pyRegRep4 import deep_get


class TestDeepGet:
    """Tests for deep_get utility function."""

    def test_returns_nested_value(self):
        data = {"doc": {"meta": {"id": "ABC-123"}}}

        assert deep_get(data, "doc", "meta", "id") == "ABC-123"

    def test_returns_default_when_key_missing(self):
        data = {"doc": {"meta": {"id": "ABC-123"}}}

        assert deep_get(data, "doc", "meta", "missing", default="n/a") == "n/a"

    def test_returns_default_when_intermediate_is_not_dict(self):
        data = {"doc": {"meta": "plain-text"}}

        assert deep_get(data, "doc", "meta", "id", default=None) is None

    def test_returns_default_when_value_is_none(self):
        data = {"doc": {"meta": {"id": None}}}

        assert deep_get(data, "doc", "meta", "id", default="fallback") == "fallback"

    def test_returns_root_data_when_keys_not_provided(self):
        data = {"doc": {"meta": {"id": "ABC-123"}}}

        assert deep_get(data) == data

