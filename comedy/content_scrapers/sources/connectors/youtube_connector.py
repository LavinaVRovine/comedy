from typing import Iterator
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .common import Connector
from googleapiclient.discovery import Resource, build

from config import ROOT_DIR

# TODO: del in prod
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
MAX_RESULTS = 50
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


class YoutubePortalConnector(Connector):

    # todo: bude to fungovat kdyz creds vyexpiruji?
    @classmethod
    def build(cls):
        ...
    # TODO: chci inherotivat z resource
    def __init__(self):
        self.service: Resource = build("youtube", "v3",
                                       credentials=credentials())

    def fetch_list_items(self, resource_, part: str, next_page_token=None, **list_kwargs) -> Iterator[dict]:
        """
        generic implementation of .list method returning a generator
        :param resource_:
        :param part:
        :param next_page_token:
        :param list_kwargs:
        :return: generator
        """
        response = resource_.list(maxResults=MAX_RESULTS, part=part, pageToken=next_page_token,
                                  **list_kwargs).execute()
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if next_page_token:
            yield from self.fetch_list_items(resource_, part=part, next_page_token=next_page_token,
                                             list_kwargs=list_kwargs)

    # def _get_all_data_from_yt(self, type_of_resource: str, part: str, **list_kwargs):
    #     # TODO: rework as a generator https://youtu.be/jItIQ-UvFI4?t=985
    #     if type_of_resource == "activities":
    #         resource_ = self.service.activities()
    #     elif type_of_resource == "channels":
    #         resource_ = self.service.channels()
    #     elif type_of_resource == "playlistItems":
    #         resource_ = self.service.playlistItems()
    #     elif type_of_resource == "subscriptions":
    #         resource_ = self.service.subscriptions()
    #     else:
    #         raise ValueError("Unexpected YT resource type")
    #     next_page_token = None
    #     results = []
    #     results =self.fetch_list_items(
    #         resource_, part, list_kwargs=list_kwargs
    #     )
    #     return results
    #     while True:
    #
    #         response = resource_.list(maxResults=MAX_RESULTS, part="snippet", pageToken=next_page_token,
    #                                   **list_kwargs).execute()
    #         next_page_token = response.get("nextPageToken", None)
    #         results += response["items"]
    #         if not next_page_token:
    #             break
    #     return results

    # def get_my_activities(self):
    #     return self._get_all_data_from_yt("activities", "snippet,contentDetails", mine=True)

    # def get_channels_uploaded_playlist_id(self, channel_id: str) -> str:
    #     """
    #     Each chanel has "uploads" playlist, ie it's uploaded videos. This gets the ID of that playlist
    #     :param channel_id: ID of a chanel who's uploads we want
    #     :return:
    #     """
    #     if channel_id[1] == "C":
    #         # Actually its the same ID just with different second character
    #         return channel_id[:1] + "U" + channel_id[2:]
    #     response = self._get_all_data_from_yt(type_of_resource="channels", part="contentDetails", id=channel_id)
    #     return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def credentials():
    token_dir_path = ROOT_DIR.joinpath("token.json")
    if token_dir_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_dir_path), SCOPES)
        except ValueError:
            creds = None
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            os.remove(token_dir_path)
            return credentials()
            creds.refresh(Request())
        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                str(ROOT_DIR.joinpath('client_secret.json')), SCOPES, )
            creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open(token_dir_path, 'w') as token:

                token.write(creds.to_json())
    return creds
