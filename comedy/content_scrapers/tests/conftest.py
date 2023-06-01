import pytest
from content_scrapers.portals.connectors.youtube_connector import YoutubePortalConnector
from content_scrapers.portals.ninegag.ninegag import NinegagSourceGroup

# todo: cant stop so the tests are super meh
# TODO: will this work in cloud?
@pytest.fixture(scope="session")
def yt_connect():
    yield YoutubePortalConnector()

@pytest.fixture
def ninegag_source():
    yield NinegagSourceGroup()
