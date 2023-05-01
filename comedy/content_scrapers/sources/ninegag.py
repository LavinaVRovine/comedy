from requests import Session as WebSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Dict
from app import models
from content_scrapers.sources.common import ContentSource
from content_scrapers.schemas.common import Tag
from content_scrapers.schemas.ninegag import NinegagAnimated as AnimatedSchema, NinegagPhoto as PhotoSchema, \
    NinegagBase, NinegagType
from content_scrapers.sources.connectors.web_connector import WebConnector
from app.models import NinegagPhoto, NinegagAnimated
import datetime
import logging



logger = logging.getLogger()


class NinegagSource(ContentSource):
    # FIXME. JOJO, tohle je ono
    INSTANCE_DB_MODEL = NinegagPhoto or NinegagAnimated
    SCHEMA_EXCLUDE = {"type": True}
    API_URL = "https://9gag.com/v1"
    @staticmethod
    def _get_my_db_portal(db: Session, ) -> models.Portal:
        return db.execute(
            select(models.Portal).where(models.Portal.slug == "ninegag")
        ).scalar()

class NinegagTagSource(NinegagSource):

    def __init__(self, source, ):
        super(NinegagTagSource, self).__init__(source=source)
        # this is a bad idea. Ill be initiating tag source, which is however a group source for top posts...

        self.tag_url = f"{self.API_URL}/tag-posts/tag/{source.source_name}"
        self.tag: Tag | None = None
        self.content: Dict[str, NinegagBase] | None = {}
        self._connector: WebSession = WebConnector()
        
    # TODO: will see how the user agent works etc
    def _fetch_new_posts(self, next_cursor: str | None = None, ) -> dict:
        if not next_cursor:
            url = self.tag_url
        else:
            url = f"{self.tag_url}?{next_cursor}"
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

    def save(self, db: Session, ):
        super(NinegagTagSource, self).save(db)
        if not self.content:
            raise ValueError

        self._save_new_content_instances_and_update(db)

    def _cast_to_db_instance(self, obj: NinegagBase):
        as_dict = self._prepare_db_instance(obj)
        if obj.type == NinegagType.photo.value:
            return NinegagPhoto(**as_dict)
        else:
            return NinegagAnimated(**as_dict)

    def _save_content_instances(self, db: Session):
        # FIXME: mam vagni pocit ze jsem idiot a nedivam se, zdali tam uz nejsou
        db.add_all(
            [self._cast_to_db_instance(v) for v in self.content.values()]
        )
        # TODO: mark content source as refreshed
        self._save_content_instances(db)
        db.commit()

    def get_content(self) -> None:
        for i, post in enumerate(self._get_new_posts()):
            published_at:datetime.datetime = datetime.datetime.utcfromtimestamp(post["creationTs"])
            post["published_at"] = published_at
            if False:
                # noinspection PyUnreachableCode
                upvotes = post["upVoteCount"]
                downvotes = post["downVoteCount"]
                comment_count = post["commentCount"]
                annotation_tags = post["annotationTags"]
                comment=post["comment"]
                creator=post["creator"]
                tags = post["tags"]
            try:
                post_id = post["id"]
                type_: str = post["type"].lower()
                if type_.lower() == "photo":
                    self.content[post_id] = PhotoSchema.parse_obj(post)
                elif type_.lower() == "animated":
                    self.content[post_id] = AnimatedSchema.parse_obj(post)
                elif type_.lower() == "article":
                    logger.debug(f"Skipping article: {post}")
                    continue
                else:
                    logger.warning(f"Unknown 9 gag type for {post}")
                    continue
            except ValueError as e:
                print(e)
                continue
        return


class NinegagGroupSource(NinegagTagSource):
    """
    I think Ill use this TOP source to populate TAGs to watch
    """

    def __init__(self, source=None):
        super(NinegagGroupSource, self).__init__(source)
        self.tag_url = f"{self.API_URL}/group-posts/group/default/type/hot"
        self.tags = []

    def _get_new_posts(self, next_cursor: str | None = None, nth_iter: int = 0):
        response_json = self._fetch_new_posts(
            next_cursor
        )
        self.tags = [Tag(**t) for t in response_json.get("tags", [])]

        return response_json["posts"]

    def _save_tags_as_sources(self, db: Session):
        from app.models.content_source import ContentSource, NinegagContentSource
        sources = []
        for t in self.tags:
            # FIXME: fakt me ty portaly serou s tema IDckama a chybejicim mappingem atp
            sources.append(
                NinegagContentSource(
                    target_system_id=t.url.replace("/tag/", ""), source_name=t.key,
                    portal_id=2,

                )
            )
        source_ids = [s.target_system_id for s in sources]
        statement = select(ContentSource.id).where(ContentSource.target_system_id.in_(
            source_ids
        ))
        existing_source_ids = db.scalars(
            statement
        ).all()
        sources_to_create = [s for s in sources if s.target_system_id not in existing_source_ids]
        if sources_to_create:
            db.add_all(
                sources_to_create
            )
            db.commit()

    def _save_new_content_instances_and_update(self, db :Session):
        ...

    def save(self, db: Session, ):
        super(NinegagGroupSource, self).save(db=db)
        self._save_new_content_instances_and_update(db)
        self._save_tags_as_sources(db)


