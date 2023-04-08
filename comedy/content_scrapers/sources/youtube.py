from datetime import datetime, timedelta
from dateutil import parser
import pytz
import os
from dataclasses import dataclass
import isodate
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

from config import DEBUGGING, ROOT_DIR
from app.models.content import YoutubeVideo, Topic
from .common import ContentSource, ReturnedContent
from sqlalchemy.orm import Session
from sqlalchemy import select
# TODO: del in prod
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
MAX_RESULTS = 50
class YoutubePortal(ContentSource):
    MAX_RESULTS = MAX_RESULTS
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    # todo: bude to fungovat kdyz creds vyexpiruji?

    def __init__(self):
        self.service: Resource = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, credentials=self.credentials)

    @property
    def credentials(self):
        token_dir_path = ROOT_DIR.joinpath("token.json")
        if token_dir_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_dir_path), self.SCOPES)
            except ValueError:
                creds = None
        else:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:

                flow = InstalledAppFlow.from_client_secrets_file(
                   str(ROOT_DIR.joinpath('client_secret.json')), self.SCOPES, )
                creds = flow.run_local_server(port=8080)

                # Save the credentials for the next run
                with open(token_dir_path, 'w') as token:

                    token.write(creds.to_json())
        return creds

    def get_my_subs(self):
        return self._get_all_data_from_yt("subscriptions", "snippet", mine=True)
    def _fetch_items(self, resource_, part:str, next_page_token=None, **list_kwargs):
        response = resource_.list(maxResults=self.MAX_RESULTS, part=part, pageToken=next_page_token,
                                      **list_kwargs).execute()
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if next_page_token:
            yield from self._fetch_items(resource_, part=part, next_page_token=next_page_token, list_kwargs=list_kwargs)
    def _get_all_data_from_yt(self, type_of_resource: str, part: str, **list_kwargs):
        # TODO: rework as a generator https://youtu.be/jItIQ-UvFI4?t=985
        if type_of_resource == "activities":
            resource_ = self.service.activities()
        elif type_of_resource == "channels":
            resource_ = self.service.channels()
        elif type_of_resource == "playlistItems":
            resource_ = self.service.playlistItems()
        elif type_of_resource == "subscriptions":
            resource_ = self.service.subscriptions()
        else:
            raise ValueError("Unexpected YT resource type")
        next_page_token = None
        results = []
        results =self._fetch_items(
            resource_, part, list_kwargs=list_kwargs
        )
        return results
        while True:

            response = resource_.list(maxResults=self.MAX_RESULTS, part=part, pageToken=next_page_token,
                                      **list_kwargs).execute()
            next_page_token = response.get("nextPageToken", None)
            results += response["items"]
            if not next_page_token:
                break
        return results

    def get_my_activities(self):
        return self._get_all_data_from_yt("activities", "snippet,contentDetails", mine=True)

    def get_channels_uploaded_playlist_id(self, channel_id: str) -> str:
        """
        Each chanel has "uploads" playlist, ie it's uploaded videos. This gets the ID of that playlist
        :param channel_id: ID of a chanel who's uploads we want
        :return:
        """
        if channel_id[1] == "C":
            # Actually its the same ID just with different second character
            return channel_id[:1] + "U" + channel_id[2:]
        response = self._get_all_data_from_yt(type_of_resource="channels", part="contentDetails", id=channel_id)
        return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


class YoutubePlaylist(YoutubePortal):

    def __init__(self, source: ContentSource):
        super(YoutubePlaylist, self).__init__()
        self.source = source
        self.playlist_id = self.source.source_id
        self.new_content = None
        self.new_content_tags = None

    def _fetch_playlist_items_page(self, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.playlistItems().list(maxResults=maxResults, part="snippet", pageToken=next_page_token,
                                                 playlistId=self.playlist_id, ).execute()

    def _fetch_video_details_page(self, video_ids, next_page_token=None, maxResults: int = MAX_RESULTS):

        return self.service.videos().list(maxResults=maxResults, part="contentDetails,topicDetails",
                                          pageToken=next_page_token,
                                          id=video_ids, ).execute()

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
            print(video_details)
            to_add_dict[video_details["id"]] = to_add_dict[video_details["id"]] | {k:v for k,v in video_details.items() if k in ("contentDetails", "topicDetails")}
        return to_add_dict

    def prepare_instances(self, response_dict: dict, topics: list[Topic]) -> list[YoutubeVideo]:
        """

        :param response_dict:
        :param topics: fairly SHORT list of possible topics
        :return:
        """
        videos = []
        for k, v in response_dict.items():
            this_vid_topics = filter(lambda x: x.wiki_link in [t for t in v["topicDetails"].get("topicCategories", [])], topics)

            videos.append(
                YoutubeVideo(target_system_id=k,
                             description=v["snippet"]["description"],
                             title=v["snippet"]["title"],
                             thumbnails=v["snippet"]["thumbnails"],
                             published_at=v["publishedAt"],
                             duration=isodate.parse_duration(v["contentDetails"]["duration"]).total_seconds(),
                             topics=list(this_vid_topics),
                             source=self.source)
            )
        return videos


    def get_content(self) -> ReturnedContent:
        # TODO: why dafuq i dont assign this to some nice instance variable and work with it afterwards?
        response_dict: dict = self._get_new_videos_since()
        # for vd in video_details["items"]:
        #     duration = vd["contentDetails"]["duration"]
        #     topic_categories: list = vd["topicDetails"]["topicCategories"]
        #     duration: timedelta = isodate.parse_duration(duration)
        # print()
        topics = []
        for v in response_dict.values():
            topics += v["topicDetails"].get("topicCategories", [])

        return ReturnedContent(content=response_dict, topics=set(topics))

