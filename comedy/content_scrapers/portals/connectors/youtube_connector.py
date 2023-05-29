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

    def fetch_list_items(self, resource_, part: str, next_page_token=None, prohibit_multiple_calls=False, **list_kwargs) -> Iterator[dict]:
        """
        generic implementation of .list method returning a generator
        :param resource_:
        :param part:
        :param next_page_token:
        :param prohibit_multiple_calls: used when testing not to consume resources
        :param list_kwargs:
        :return: generator
        """
        response = resource_.list(maxResults=MAX_RESULTS, part=part, pageToken=next_page_token,
                                  **list_kwargs).execute()
        yield from response["items"]
        next_page_token = response.get("nextPageToken", None)
        if prohibit_multiple_calls:
            next_page_token = None
        if next_page_token:
            yield from self.fetch_list_items(resource_, part=part, next_page_token=next_page_token,
                                             list_kwargs=list_kwargs)


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
            try:
                creds.refresh(Request())
            except BaseException:
                os.remove(token_dir_path)
                return credentials()
        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                str(ROOT_DIR.joinpath('client_secret.json')), SCOPES, )
            creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open(token_dir_path, 'w') as token:

                token.write(creds.to_json())
    return creds
