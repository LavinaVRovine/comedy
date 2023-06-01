import pytest
import pytest_mock

from content_scrapers import portals
print()

@pytest.fixture
def youtube_playlist_source(mocker, yt_connect):
    mm = mocker.Mock()

    yield portals.YoutubeUploadedPlaylist(connector=yt_connect)


# TODO: mock etc
def test_youtube_sets_content(
        youtube_playlist_source,
        mocker):
    mm = mocker.Mock()
    # TODO: ha ten mock fubnguje
    #mocker.patch("content_scrapers.portals.connectors.youtube_connector.YoutubePortalConnector.__init__",
    #             return_value=None)
    #mocker.patch("content_scrapers.portals.connectors.youtube_connector.YoutubePortalConnector.fetch_list_items", return_value=mm)

    print(mm)
    youtube_playlist_source.get_content()
    assert youtube_playlist_source.content, "yt scraper failed to scrape top content"

@pytest.fixture(scope="session")
def youtube_video_source(yt_connect):
    yield portals.YoutubeVideoPortal("PLRv5q2ew_zJt4Wbynk2fGBBldb1qzB1HH", connector=yt_connect)


def test_youtube_video_sets_content(
        youtube_video_source,
        mocker):
    #mm = mocker.Mock()
    youtube_video_source.get_content()
    assert len(youtube_video_source.content) >0, "x"
