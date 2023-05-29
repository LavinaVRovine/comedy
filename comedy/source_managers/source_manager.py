import logging
from abc import ABC, abstractmethod
from content_scrapers.portals.common import ContentPortal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import SessionLocalApp

from app import models


from content_scrapers.schemas.common import Tag, Topic
from config import DEBUGGING
from datetime import datetime, timedelta
logger = logging.getLogger()


class SourceManager(ABC):
    """
    class mapping scraper to app db model
    """
    def __init__(self, source: models.ContentSource | str, ):
        # TODO: not certain whether i want it to be an instance var
        self.topics_as_db_instances = []
        self.source: models.ContentSource = self._init_source(source)

    def _prohibit_refresh(self):
        """
        To save resources, we probably wont want to refresh every single time
        :return:
        """
        if DEBUGGING:
            return False
        # TODO: TZ thing
        if self.source.last_checked_at and self.source.last_checked_at <= datetime.utcnow().replace(
                tzinfo=None) - timedelta(days=1):
            logger.warning("Refresh prohibited as the source was refreshed less than a X ago")
            return True
        return False

    def refresh(self, db: Session, ) -> None:

        """

        :param db:
        :return:
        """

        if self._prohibit_refresh():
            return
        # FIXMe: ja si myslim ze tady budu potrebovat passovat ten scraper class
        #self.save(db)
        return

    @staticmethod
    def _init_source(source) -> models.ContentSource:
        """
        Just a small helper to support either string or db instance. Probably not really needed
        as the model shall be always chosen but still
        :param source:
        :return:
        """
        if not isinstance(source, str):
            return source

        db = SessionLocalApp()
        statement = select(models.ContentSource).where(models.ContentSource.target_system_id == source)
        x = db.scalar(statement)
        if not x:
            raise ValueError
        db.close()
        return x
    @abstractmethod
    def save(self, *, source_scraper: ContentPortal, db: Session, ) -> list[models.ContentSource]:
        raise NotImplementedError
        if not source_scraper.content:
            source_scraper.get_content()
        return self._save_new_content_instances_and_update(db, )

    def _save_new_content_instances_and_update(self, db: Session, db_instances):
        statement = select(models.Content).where(models.Content.target_system_id.in_(
            [s.target_system_id for s in db_instances]
        ))

        existing_contents = db.execute(
            statement
        ).scalars().all()

        existing_ids = [x.target_system_id for x in existing_contents]
        new_contents = [x for x in db_instances if x.target_system_id not in existing_ids]

        logger.debug(f"Found {len(existing_ids)} existing contents")
        if new_contents:
            logger.debug(f"Creating {len(new_contents)} new contents")
            db.add_all(new_contents)
            db.commit()

        self._update_source_checked_datetime(db)
        db.commit()
        logger.debug("Successfully saved new instances o")

        return existing_contents + new_contents

    def _update_source_checked_datetime(self, db: Session):
        self.source.last_checked_at = datetime.utcnow().replace(
                tzinfo=None)
        db.add(
            self.source
        )

    def _save_set_topics(self, db: Session, topics_schemas: list[Tag | Topic]) -> None:
        """
        Save tags/topics
        :param db:
        :param topics_schemas:
        :return:
        """
        if not topics_schemas:
            return
        statement = select(models.Topic).where(models.Topic.key.in_([t.key for t in topics_schemas]))
        topics = db.scalars(statement).all()

        existing_topic_names = [t.key for t in topics]

        topics_to_be_created = [
            models.Topic(key=t.key, url=t.url, ) for t in
            topics_schemas if t.key not in existing_topic_names]
        db.add_all(topics_to_be_created)
        db.commit()
        self.topics_as_db_instances = list(topics) + topics_to_be_created
        return


