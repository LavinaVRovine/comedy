from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from source_managers.source_manager import SourceManager
from content_scrapers.portals.ninegag.ninegag import NinegagSourceTag, NinegagSourceGroup
from content_scrapers import schemas
from app.supported_portals import SupportedPortals


class SourceManagerNinegag(SourceManager):

    def _save_tags_as_sources(self, db: Session, source_scraper: [NinegagSourceTag | NinegagSourceGroup]) -> None:
        """
        I am saving all the tags as sources so they become sources themselves and are themselves
        scraped on the next refresh run
        :param db:
        :param source_scraper:
        :return:
        """
        sources = []
        for t in source_scraper.topics:
            sources.append(
                models.NinegagContentSource(
                    target_system_id=t.url.replace("/tag/", ""), source_name=t.key,
                    portal_id=SupportedPortals.ninegag.id,

                )
            )
        source_ids = [s.target_system_id for s in sources]
        statement = select(models.ContentSource.target_system_id).where(models.ContentSource.target_system_id.in_(
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

    def prepare_models(self, source_scraper: NinegagSourceTag | NinegagSourceGroup,)->list[models.NinegagAnimated|models.NinegagPhoto]:
        all_contents = []
        for c in source_scraper.content.values():
            if isinstance(c, schemas.NinegagAnimated):
                m = models.NinegagAnimated.from_schema(c, source=self.source)
            else:
                m = models.NinegagPhoto.from_schema(c, source=self.source)
            db_topics = []
            for schema_tag in c.tags:
                for topic in self.topics_as_db_instances:
                    if topic.key == schema_tag.key:
                        db_topics.append(topic)
            # TODO: figure out how to solve topics in model
            m.topics = db_topics
            all_contents.append(m)
        return all_contents

    def save(self, *, db: Session, source_scraper: NinegagSourceTag | NinegagSourceGroup, ):
        # FIXME: fixni to, vlastne nevim zdali chci vzdy pridavat tagy jakou sources + to ze ten Tag source to jaksi nema
        if not source_scraper.content:
            raise ValueError
        self._save_tags_as_sources(db, source_scraper)
        self._save_set_topics(db, topics_schemas=source_scraper.topics)
        all_contents = self.prepare_models(source_scraper)
        self._save_new_content_instances_and_update(db, db_instances=all_contents)
