import os

import pytest

import mediawiki_abusefilter

pytestmark = pytest.mark.integration


def test_local_mediawiki():
    url = os.getenv("MW_TEST_URL")
    username = os.getenv("MW_TEST_USERNAME")
    password = os.getenv("MW_TEST_PASSWORD")

    if not url or not username or password is None:
        pytest.skip("set MW_TEST_URL, MW_TEST_USERNAME and MW_TEST_PASSWORD")

    filters = mediawiki_abusefilter.Filters(url, username=username, password=password)
    filter = filters.create("pytest integration filter", "false", notes="pytest")
    filter.edit(
        rules="false & page_namespace == 0 & user_editcount >= 0",
        description="pytest edited filter",
        notes="pytest edited",
        enabled=True,
        public=False,
        actions={
            "warn": "abusefilter-warning",
            "disallow": "abusefilter-disallowed",
            "blockautopromote": True,
            "block": {"talk": True, "anonymous": "1 day", "user": "1 day"},
            "tag": ["pytest-test"],
            "throttle": {"count": 5, "period": 120, "groups": "user"},
        },
        verify=True,
    )
    filter.refresh()
    assert filter.description == "pytest edited filter"
    assert filter.rules == "false & page_namespace == 0 & user_editcount >= 0"
    assert filter.notes == "pytest edited"
    assert filter.enabled is True
    assert filter.public is False
    assert "warn" in filter.actions
    assert "disallow" in filter.actions
    assert "block" in filter.actions
    assert "tag" in filter.actions
    assert "throttle" in filter.actions
