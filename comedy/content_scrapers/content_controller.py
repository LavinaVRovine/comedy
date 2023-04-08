import logging

import pytz
import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.content_source import ContentSource as SourceModel
from content_scrapers.sources.common import ContentSource, ReturnedContent
from app.models.content import Content, Topic
from content_scrapers.sources.youtube import YoutubePlaylist
from app.db.session import SessionLocalApp, SessionLocalAppAsync
from datetime import datetime, timedelta
from config import DEBUGGING
logger = logging.getLogger()


class ContentController:
    # TODO:
    def __init__(self, content_source_to_refresh: SourceModel, ):
        self.content_source_to_refresh = content_source_to_refresh
        self.content_refresher = self._decide_scraper()

    def _decide_scraper(self) -> ContentSource:
        if not self.content_source_to_refresh.portal.slug == "youtube":
            source_refresher_model = None
            raise NotImplementedError
        return YoutubePlaylist(self.content_source_to_refresh)

    def _prohibit_refresh(self):

        if DEBUGGING:
            return False
        # TODO: TZ thing
        if self.content_source_to_refresh.last_checked_at and self.content_source_to_refresh.last_checked_at <= datetime.utcnow().replace(
                tzinfo=None) - timedelta(days=1):
            logger.warning("Refresh prohibited as the source was refreshed less than a X ago")
            return True
        return False
    def refresh_no_return(self):
        from app.db.session import SessionLocalApp, engine

        self.refresh(
            SessionLocalApp()
        )

        ...
    def _add_topic_to_content(self, db: Session, contents: list[Content]):
        for c in contents:
            print()
    def refresh(self, db: Session, ) -> list[Content]:
        # TODO: i freaking hate the creation and search of topics. Its dumb as fuck
        #  but i dunno how to do it better
        """

        :param db:
        :return:
        """

        if self._prohibit_refresh():
            return []
        content: ReturnedContent = self.content_refresher.get_content()
        to_add = content.content
        if content.topics:
            statement = select(Topic).where(Topic.wiki_link.in_(content.topics))
            topics = db.scalars(statement).all()
            existing_topic_names = [t.wiki_link for t in topics]
            topics_to_be_created = [Topic(wiki_link=t) for t in content.topics if t not in existing_topic_names]
            db.add_all(topics_to_be_created)
            db.commit()

            all_topics = list(topics) + topics_to_be_created
        else:
            all_topics = []
        to_add = self.content_refresher.prepare_instances(to_add, all_topics)

        try:
            #db.bulk_save_objects(to_add)

            db.add_all(to_add)
            # TODO: how about we switch to NEWEST content DT rather than refresh date?
            self.content_source_to_refresh.last_checked_at = max([m.published_at for m in to_add])#datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)

            db.commit()
            return to_add

        except sqlalchemy.exc.IntegrityError as e:
            # there is an implicit assumption in refresh, that we are refreshing only new videos?
            # but theoretically something might go wrong?
            db.rollback()
            existing_titles = [x.title for x in self.content_source_to_refresh.contents]
            to_add = [x for x in to_add if x.title not in existing_titles]
            if not to_add:
                return to_add
            db.add_all(to_add)
            self.content_source_to_refresh.last_checked_at = max([m.published_at for m in to_add])#datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)
            return to_add


if __name__ == '__main__':
    with SessionLocalApp() as session:
        lala = session.query(SourceModel).where(SourceModel.id == 1).one()
        controller = ContentController(lala)
        controller.refresh(session)
    print()