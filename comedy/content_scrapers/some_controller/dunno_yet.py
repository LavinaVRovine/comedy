from content_scrapers.sources.ninegag_new.ninegag import NinegagSourceGroup, NinegagSourceTag
from sqlalchemy.orm import Session
from content_scrapers.sources.common_new import ContentSource
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.content_source import ContentSource as ContentSourceModel
from app import models
from content_scrapers.sources.connectors.common import Connector
import datetime
from content_scrapers.schemas.common import Tag, Topic




class SourceManager:

    def save(self, source_scraper: ContentSource, db: Session, ) -> list[ContentSourceModel]:

        if not source_scraper.content:
            source_scraper.get_content()
        return self._save_new_content_instances_and_update(db)

    def _save_new_content_instances_and_update(self, db: Session, db_instances):


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

        try:
            if new_sources:
                db.add_all(new_sources)
                db.commit()
        except BaseException:
            print()

        self._update_source_checked_datetime(db)
        db.commit()
        # noinspection PyUnresolvedReferences
        return existing_sources + new_sources


class SourceManagerNinegag(SourceManager):



    def _prepare_db_instance(self, obj) -> dict:
        parsed = super(NinegagTagSource, self)._prepare_db_instance(obj)
        try:
            parsed["duration"] = obj.get_duration()
        except AttributeError:
            pass
        statistics = {}
        for k in ("likes", "dislikes", "comments",):
            statistics[k] = parsed.pop(k)

        parsed["statistics"] = [
            models.ContentStatistics(**statistics)
        ]
        return parsed

    # def _cast_to_db_instance(self, obj: NinegagBase):
    #     as_dict = self._prepare_db_instance(obj)
    #     if obj.type == NinegagType.photo.value:
    #         return NinegagPhoto(**as_dict)
    #     else:
    #         return NinegagAnimated(**as_dict)

    def _save_content_instances(self, db: Session):
        # FIXME: mam vagni pocit ze jsem idiot a nedivam se, zdali tam uz nejsou
        db.add_all(
            [self._cast_to_db_instance(v) for v in self.content.values()]
        )
        # TODO: mark content source as refreshed
        #self._save_content_instances(db)
        db.commit()



    def save(self, source_scraper: [NinegagSourceTag | NinegagSourceGroup], db:Session):

        tags = []
        model_instances: list[models.Content] = [c.cast_to_db_instance() for c in source_scraper.content.values()]
        for c in source_scraper.content.values():
            m: models.Content = c.cast_to_db_instance()


        if not source_scraper.content:
            raise ValueError

        self._save_new_content_instances_and_update(db)
