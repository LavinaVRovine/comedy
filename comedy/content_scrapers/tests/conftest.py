import pytest

from content_scrapers.portals.ninegag.ninegag import NinegagSourceGroup


@pytest.fixture
def ninegag_source():
    yield NinegagSourceGroup()
