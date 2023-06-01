from typing import cast
from requests import Session as WebSession
from abc import ABC
from content_scrapers.schemas.common import Tag, Topic
from content_scrapers.schemas.ninegag import NinegagAnimated as AnimatedSchema, NinegagPhoto as PhotoSchema, \
    NinegagBase, NinegagType
from content_scrapers import schemas
from content_scrapers.portals.connectors.web_connector import WebConnector
import datetime
import logging
from app.utils import parse_key_from_url
from content_scrapers.portals.common import ContentPortal

logger = logging.getLogger()



class NinegagPortal(ContentPortal, ABC):
    API_URL = "https://9gag.com/v1"

    def __init__(self):
        super(NinegagPortal, self).__init__()
        self._connector: WebSession = WebConnector()
        self.content = cast(
            dict[str, schemas.NinegagPhoto | schemas.NinegagAnimated], self.content
        )

    @property
    def url(self):

        if not hasattr(self, "_url") or not self._url:
            raise ValueError("define _url")
        return self._url

    def _fetch_new_posts(self, next_cursor: str | None = None, ) -> dict:
        if not next_cursor:
            url = self.url
        else:
            url = f"{self.url}?{next_cursor}"
        response = self.connector.get(url, )
        assert response.status_code == 200
        return response.json()["data"]
    def _get_new_posts(self, next_cursor: str | None = None, nth_iter: int = 0):
        response_json = self._fetch_new_posts(
            next_cursor
        )
        if not self.tag:
            self.tag = Tag(**response_json["tag"])

        yield from response_json["posts"]
        next_page_cursor = response_json.get("nextCursor", None)
        # TODO: might detect on creation date?
        #  ALSO iam not certain it even returns different results with that cursor thingy
        if next_page_cursor and nth_iter < 0:
            yield from self._get_new_posts(next_page_cursor, nth_iter + 1)


    def get_content(self) -> None:
        for i, post in enumerate(self._get_new_posts()):
            published_at: datetime.datetime = datetime.datetime.utcfromtimestamp(post["creationTs"])
            post["published_at"] = published_at
            try:
                post_id = post["id"]
                type_: str = post["type"].lower()
                if type_.lower() == "photo":
                    self.content[post_id] = PhotoSchema.parse_obj(post)
                elif type_.lower() == "animated":
                    post_parsed = AnimatedSchema.parse_obj(post)
                    self.content[post_id] = post_parsed
                elif type_.lower() == "article":
                    logger.debug(f"Skipping article: {post}")
                    continue
                else:
                    logger.warning(f"Unknown 9 gag type for {post}")
                    continue
                for t in self.content[post_id].tags:
                    t.key = parse_key_from_url(t.url)
                    if t not in self.topics:
                        self.topics.append(t)
            except ValueError as e:
                print(e)
                continue
        return


class NinegagSourceTag(NinegagPortal):
    def __init__(self, source_name: str):
        super(NinegagSourceTag, self).__init__()
        self.source_name: str = source_name
        self._url = f"{self.API_URL}/tag-posts/tag/{source_name}"


class NinegagSourceGroup(NinegagPortal):
    def __init__(self):
        super(NinegagSourceGroup, self).__init__()
        self.source_name: str = "top"
        self._url = f"{self.API_URL}/group-posts/group/default/type/{self.source_name}"
    # FIXME: tohle je zase co pici
    def _get_new_posts(self, next_cursor: str | None = None, nth_iter: int = 0):
        response_json = self._fetch_new_posts(
            next_cursor
        )
        # FIXME: vyres to ze je tag, tags a topics
        self.tags = [Tag(**t) for t in response_json.get("tags", [])]

        return response_json["posts"]
