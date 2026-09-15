import pytest

from mediawiki_abusefilter.rules import apply_rules
from mediawiki_abusefilter.exceptions import RuleEditError


def test_replace_all():
    assert apply_rules("foo foo", replace=("foo", "bar")) == "bar bar"


def test_replace_once():
    assert apply_rules("foo foo", replace=("foo", "bar", 1)) == "bar foo"


def test_multiple_replacements():
    assert apply_rules("foo abc foo", replace=[("foo", "bar"), ("abc", "xyz")]) == "bar xyz bar"


def test_append_prepend_remove():
    assert apply_rules("x & foo", append=" & bar", remove="x & ", prepend="prefix & ") == "prefix & foo & bar"


def test_remove_many():
    assert apply_rules("foo abc foo", remove=["foo", "abc"]) == "  "


def test_regex():
    assert apply_rules("user_editcount < 10", regex=(r"user_editcount\s*<\s*\d+", "user_editcount < 100")) == "user_editcount < 100"


def test_strict_missing():
    with pytest.raises(RuleEditError):
        apply_rules("foo", replace=("bar", "baz"))


def test_non_strict_missing():
    assert apply_rules("foo", replace=("bar", "baz"), strict=False) == "foo"
