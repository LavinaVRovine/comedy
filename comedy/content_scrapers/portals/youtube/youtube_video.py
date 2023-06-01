import datetime
from typing import cast
import isodate
import pytz
from dateutil import parser

from config import DEBUGGING
from content_scrapers import schemas
from content_scrapers.schemas.youtube import YoutubeVideo
from content_scrapers.portals.common import ContentPortal
from content_scrapers.portals.connectors.youtube_connector import MAX_RESULTS, YoutubePortalConnector
from app.utils import parse_key_from_url
from content_scrapers.schemas.common import Topic


class YoutubeVideoPortal(ContentPortal):

    def __init__(self, playlist_id: str, source_last_checked_at: datetime.datetime | None = None, connector=YoutubePortalConnector()):
        super(YoutubeVideoPortal, self).__init__()
        self._connector = connector
        self.service = self.connector.service
        self.last_checked_at = source_last_checked_at
        self.playlist_id = playlist_id
        self.content = cast(
            dict[str, schemas.YoutubeVideo], self.content
        )

    def _fetch_playlist_items_page(self, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.playlistItems().list(maxResults=maxResults, part="snippet", pageToken=next_page_token,
                                                 playlistId=self.playlist_id, ).execute()

    def _fetch_video_details_page(self, video_ids, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.videos().list(maxResults=maxResults, part="contentDetails,topicDetails",
                                          pageToken=next_page_token,
                                          id=video_ids, ).execute()
    # @staticmethod
    # def _get_my_db_portal(db: Session, ) -> models.Portal:
    #     return db.execute(
    #         select(models.Portal).where(models.Portal.slug == "youtube")
    #     ).scalar()

    def _get_videos(self, page_token=None) -> list[dict]:
        response = self._fetch_playlist_items_page(next_page_token=page_token)
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if next_page_token:
            yield from self._get_videos(page_token=next_page_token, )

    def _get_video_details(self, video_ids: list[str], page_token=None) -> list[dict]:

        response = self._fetch_video_details_page(video_ids=video_ids, next_page_token=page_token)
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if next_page_token:
            yield from self._get_video_details(page_token=next_page_token, video_ids=video_ids, )

    def _get_new_videos_since(self, ) -> dict:
        """
        Get "new videos". THis is '2' calls, one for playlist-list and another for details.
        Getting just ids first would work, but there is no timestamp in returned, hence would not be able to limit
        so this way seems better for quota?
        :return:
        """

        to_add_dict = {}
        for i, v in enumerate(
                self._get_videos()
        ):
            published_at = parser.parse(v["snippet"]["publishedAt"])
            v["publishedAt"] = published_at
            video_id = v["snippet"]["resourceId"]["videoId"]

            if not DEBUGGING:
                print("CARE WE ARE ALWAYS RETURNING EVEN EXISTING ONES TO KNOW THE REFRESH WORKS?")
                # TODO: this pytz and utc has to be done better
                if self.last_checked_at and published_at <= self.last_checked_at.astimezone(pytz.utc):
                    break
            to_add_dict[video_id] = v
            if i > 10:
                print("HARDCODED stopiter")
                break
        additional_details = self._get_video_details([video_id for video_id in to_add_dict.keys()])
        for video_details in additional_details:
            video_details["contentDetails"]["duration"] = isodate.parse_duration(video_details["contentDetails"]["duration"]).total_seconds()
            to_add_dict[video_details["id"]] = to_add_dict[video_details["id"]] | {k:v for k,v in video_details.items() if k in ("contentDetails", "topicDetails")}
        return to_add_dict

    def get_content(self) -> None:
        response_dict: dict = self._get_new_videos_since()

        for k, v in response_dict.items():
            yt_video = YoutubeVideo.parse_obj(v)
            self.content[k] = yt_video
            try:
                for t in yt_video.topic_details.topic_categories:

                    t = Topic(key=parse_key_from_url(t), url=t)
                    if t not in self.topics:
                        self.topics.append(t)
            except AttributeError:
                pass
