import os

import pytest

import mediawiki_abusefilter

pytestmark = pytest.mark.integration


def test_private_to_public():
    url = os.getenv("MW_TEST_URL")
    username = os.getenv("MW_TEST_USERNAME")
    password = os.getenv("MW_TEST_PASSWORD")
    filter_id = os.getenv("MW_TEST_PRIVATE_FILTER_ID")

    if not url or not username or password is None or not filter_id:
        pytest.skip("set MW_TEST_URL, MW_TEST_USERNAME, MW_TEST_PASSWORD and MW_TEST_PRIVATE_FILTER_ID")

    filters = mediawiki_abusefilter.Filters(url, username=username, password=password)
    filter = filters.get(int(filter_id))
    filter.edit(public=True)
    filter.refresh()
    assert filter.public is True
