import pytest
import pytest_mock

from content_scrapers import portals
print()

@pytest.fixture
def youtube_playlist_source():
    yield portals.YoutubeUploadedPlaylist()



def test_ninegag_scrapes_top_category(
        youtube_playlist_source,
        mocker):
    mm = mocker.Mock()

    mocker.patch("content_scrapers.portals.connectors.youtube_connector.YoutubePortalConnector.__init__",
                 return_value=None)
    mocker.patch("content_scrapers.portals.connectors.youtube_connector.YoutubePortalConnector.fetch_list_items", return_value=mm)
    breakpoint()
    print(mm)
    #youtube_playlist_source.get_content()
    #assert len(ninegag_source.content) == 10, "Ninegag scraper failed to scrape top content"
