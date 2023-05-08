from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.content_source import ContentSource as ContentSourceModel
from app import models
from content_scrapers.sources.connectors.common import Connector
import datetime
from content_scrapers.schemas.common import Tag, Topic

class ContentSource(ABC):
    INSTANCE_DB_MODEL = None
    SCHEMA_EXCLUDE = {}

    def __init__(self, source: ContentSourceModel):
        self.source = source
        self.raw_content = None
        self.content: dict[str, dict] = {}
        self._connector: Connector = None
        self.topics: list[Tag|Topic] = []

    @property
    def connector(self):
        if not self._connector:
            raise ValueError("Define connector")
        return self._connector

    @abstractmethod
    def get_content(self):
        raise NotImplementedError

    def _save_set_topics(self, db: Session) -> None:
        if not self.topics:
            return
        statement = select(models.Topic).where(models.Topic.key.in_([t.key for t in self.topics]))
        topics = db.scalars(statement).all()

        existing_topic_names = [t.key for t in topics]

        topics_to_be_created = [
            models.Topic(key=t.key, url=t.url, ) for t in
            self.topics if t.key not in existing_topic_names]
        db.add_all(topics_to_be_created)
        db.commit()
        self.topics_as_db_instances = list(topics) + topics_to_be_created
        return

    @staticmethod
    @abstractmethod
    def _get_my_db_portal(db: Session):
        """
        I want to be explicit which portal instance it is. God i hate this
        :param db:
        :return:
        """
        raise NotImplementedError
    def save(self, db: Session, ) -> list[ContentSourceModel]:
        """
        Save scraped content into DB.
        Optionally get the content as well
        :param db:
        :return: New instances + NON-UPDATED already existing instances of content
        """
        if not self.content:
            self.get_content()
        return self._save_new_content_instances_and_update(db)

    def _prepare_db_instance(self, obj) -> dict:
        """
        Dump obj into a dict which is to be used to init the DB instance.
        There just has to be some nicer way than this...
        :param obj:
        :return:
        """
        as_dict = obj.dict(by_alias=True, exclude=self.SCHEMA_EXCLUDE)
        as_dict["source"] = self.source
        return as_dict

    def _cast_to_db_instance(self, obj):
        """
        Create DB model instance
        :param obj: pydantic schema instance
        :return:
        """
        return self.INSTANCE_DB_MODEL(**self._prepare_db_instance(obj))

    def _update_source_checked_datetime(self, db: Session):
        self.source.last_checked_at = datetime.datetime.utcnow().replace(
                tzinfo=None)
        db.add(
            self.source
        )

    def _save_new_content_instances_and_update(self, db: Session):
        from app import models
        db_instances = [self._cast_to_db_instance(v) for v in self.content.values()]
        # FIXME: no ja se dotazuji na photo a pritom jaksi mam i animated ze....
        # a taky bych se mohl podivat proc se to vlastne duplikuje
        statement = select(models.Content).where(models.Content.target_system_id.in_(
            [s.target_system_id for s in db_instances]
        ))

        existing_sources = db.execute(
            statement
        ).scalars().all()

        existing_ids = [x.target_system_id for x in existing_sources]
        new_sources = [x for x in db_instances if x.target_system_id not in existing_ids]


        if new_sources:
            db.add_all(new_sources)
            db.commit()

        self._update_source_checked_datetime(db)
        db.commit()
        # noinspection PyUnresolvedReferences
        return existing_sources + new_sources
