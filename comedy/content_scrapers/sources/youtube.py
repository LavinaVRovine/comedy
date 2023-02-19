from datetime import datetime
from dateutil import parser

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource
from comedy.config import ROOT_DIR
from app.models.source import ContentSource
from app.models.content import YoutubeVideo
from .common import ContentSource

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
        self.playlist_id = self.source.id

    def _fetch_playlist_items_page(self, next_page_token=None, maxResults:int=MAX_RESULTS):

        return self.service.playlistItems().list(maxResults=maxResults, part="snippet", pageToken=next_page_token,
                                                 playlistId=self.playlist_id, ).execute()

    def _get_videos(self, page_token=None) -> list[dict]:
        response = self._fetch_playlist_items_page(next_page_token=page_token )
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if next_page_token:
            yield from self._get_videos(page_token=next_page_token, )

    def _get_new_videos_since(self, ):
        to_add = []

        for i, v in enumerate(
                self._get_videos()
        ):
            published_at = parser.parse(v["snippet"]["publishedAt"])
            v["publishedAt"] = published_at
            if self.source.last_checked_at and published_at >= self.source.last_checked_at:
                break
            # if i>10:
            #     print("stopiter")
            #     break
            to_add.append(
                v
            )
            return to_add

    def get_content(self) -> list[YoutubeVideo]:
        vids = self._get_new_videos_since()
        return [
            YoutubeVideo(id=v["snippet"]["resourceId"]["videoId"],
                         description=v["snippet"]["description"],
                         title=v["snippet"]["title"],
                         thumbnails=v["snippet"]["thumbnails"],
                         published_at=v["published_at"]) for v in vids
        ]


if __name__ == '__main__':
    youtube_source = YoutubePortal()
    bittersteel_playlist_id = "UU4tWW-toq9KKo-HL3S8D23A"
    bitterstel_channel_id = 'UC4tWW-toq9KKo-HL3S8D23A' # = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    #uploads_playilis = youtube_source.get_channels_uploaded_playlist_id(channel_id=bitterstel_channel_id)

    vs = youtube_source.get_videos(bittersteel_playlist_id)
    print()
    # TODO: this will probably have to be used once not scripting but using server
    # YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"


    # if False:
    #
    #     # Use the client_secret.json file to identify the application requesting
    #     # authorization. The client ID (from that file) and access scopes are required.
    #     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #         'client_secret.json',
    #         scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])
    #
    #     # Indicate where the API server will redirect the user after the user completes
    #     # the authorization flow. The redirect URI is required. The value must exactly
    #     # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    #     # configured in the API Console. If this value doesn't match an authorized URI,
    #     # you will get a 'redirect_uri_mismatch' error.
    #     flow.redirect_uri = 'https://www.example.com/oauth2callback'
    #
    #     # Generate URL for request to Google's OAuth 2.0 server.
    #     # Use kwargs to set optional request parameters.
    #     authorization_url, state = flow.authorization_url(
    #         # Enable offline access so that you can refresh an access token without
    #         # re-prompting the user for permission. Recommended for web server apps.
    #         access_type='offline',
    #         # Enable incremental authorization. Recommended as a best practice.
    #         include_granted_scopes='true')