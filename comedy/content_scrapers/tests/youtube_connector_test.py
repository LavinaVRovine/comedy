from content_scrapers.portals.connectors.youtube_connector import YoutubePortalConnector
import pytest

# todo: cant stop so the tests are super meh
# TODO: will this work in cloud?


@pytest.fixture(scope="module")
def yt_connect():
    yield YoutubePortalConnector()


def test_youtube_can_connect_to_my_acc_test(yt_connect):
    assert yt_connect


def test_youtube_gets_my_subscriptions_test(yt_connect):
    items = yt_connect.fetch_list_items(
        yt_connect.service.subscriptions(), "snippet", mine=True
    )
    assert items
