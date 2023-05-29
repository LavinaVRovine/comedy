import isodate
import pytz
import sqlalchemy.exc
from dateutil import parser
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import YoutubeVideo
from app.models.content import Topic
from app import models
from config import DEBUGGING
from content_scrapers.schemas.youtube import YoutubeVideoBase
from content_scrapers.portals.common import ContentPortal
from content_scrapers.portals.connectors.youtube_connector import MAX_RESULTS, YoutubePortalConnector
from app.utils import parse_key_from_url
from content_scrapers.schemas.common import Topic

class YoutubeVideoPortal(ContentPortal):
    INSTANCE_DB_MODEL = YoutubeVideo
    SCHEMA_EXCLUDE = {"kind": True, "topic_details": True, }

    def __init__(self, source):
        super(YoutubeVideoPortal, self).__init__(source)
        self._connector = YoutubePortalConnector()
        self.service = self.connector.service
        self.playlist_id = self.source.target_system_id

        self.topics_as_db_instances: list[Topic] = []

    def _fetch_playlist_items_page(self, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.playlistItems().list(maxResults=maxResults, part="snippet", pageToken=next_page_token,
                                                 playlistId=self.playlist_id, ).execute()

    def _fetch_video_details_page(self, video_ids, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.videos().list(maxResults=maxResults, part="contentDetails,topicDetails",
                                          pageToken=next_page_token,
                                          id=video_ids, ).execute()
    @staticmethod
    def _get_my_db_portal(db: Session, ) -> models.Portal:
        return db.execute(
            select(models.Portal).where(models.Portal.slug == "youtube")
        ).scalar()
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
                if self.source.last_checked_at and published_at <= self.source.last_checked_at.astimezone(pytz.utc):
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



    def _prepare_db_instance(self, obj) -> dict:
        as_dict = obj.dict(by_alias=False, exclude=self.SCHEMA_EXCLUDE)
        as_dict["source"] = self.source
        as_dict.pop("id")
        as_dict["target_system_id"] = as_dict["snippet"]["resource_id"]["video_id"]
        as_dict = as_dict | as_dict.pop("snippet")
        as_dict = as_dict | as_dict.pop("content_details")
        as_dict.pop("resource_id")
        return as_dict

    def _save_new_content_instances_and_update(self, db: Session, ):
        videos = []
        for k, v in self.content.items():
            vid = self._cast_to_db_instance(v)
            try:
                this_vid_topics = filter(lambda x: x.url in [t for t in v.topic_details.topic_categories],
                                     self.topics_as_db_instances)
                vid.topics = list(this_vid_topics)
            except AttributeError:
                pass
            finally:
                videos.append(vid)

        try:
            db.add_all(videos)
            # TODO: how about we switch to NEWEST content DT rather than refresh date?
            self.source.last_checked_at = max(
                [m.published_at for m in videos])  # datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)
            db.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # there is an implicit assumption in refresh, that we are refreshing only new videos?
            # but theoretically something might go wrong?
            db.rollback()
            existing_titles = [x.title for x in self.source.contents]
            to_add = [x for x in videos if x.title not in existing_titles]
            if not to_add:
                return to_add
            db.add_all(to_add)
            self.source.last_checked_at = max(
                [m.published_at for m in to_add])  # datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)

    def save(self, db: Session, ):
        if not self.content:
            self.get_content()
        self._save_set_topics(db)
        super(YoutubeVideoPortal, self).save(db)

    def get_content(self) -> None:
        response_dict: dict = self._get_new_videos_since()

        for k, v in response_dict.items():
            yt_video = YoutubeVideoBase.parse_obj(v)
            self.content[k] = yt_video
            try:
                for t in yt_video.topic_details.topic_categories:

                    t = Topic(key=parse_key_from_url(t), url=t)
                    if t not in self.topics:
                        self.topics.append(t)
            except AttributeError:
                pass
