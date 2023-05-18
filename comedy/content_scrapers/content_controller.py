import logging

import pytz
import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.content_source import ContentSource as SourceModel
from content_scrapers.sources.common import ContentSource
from app.models.content import Content, Topic
from content_scrapers.sources import YoutubeVideoSource, NinegagTagSource
from content_scrapers.sources.ninegag import NinegagGroupSource
from content_scrapers.sources.youtube.youtube_playlist import YoutubeUploadedPlaylist

from app.db.session import SessionLocalApp
from datetime import datetime, timedelta
from config import DEBUGGING
logger = logging.getLogger()


class ContentBridge:
    # TODO:
    def __init__(self, content_source_to_refresh: SourceModel, ):
        self.content_source_to_refresh = content_source_to_refresh
        self.content_refresher = self.decide_content_refresher()

    def decide_content_refresher(self) -> ContentSource:
        return self.decide_scraper_class(self.content_source_to_refresh.portal.slug, self.content_source_to_refresh)
        if self.content_source_to_refresh.portal.slug == "ninegag":
            return NinegagTagSource(self.content_source_to_refresh)
        if not self.content_source_to_refresh.portal.slug == "youtube":
            source_refresher_model = None
            raise NotImplementedError
        return YoutubeVideoSource(self.content_source_to_refresh)

    @staticmethod
    def decide_portal_connector_class(portal_slug: str):
        if portal_slug == "youtube":
            return YoutubeUploadedPlaylist

        raise NotImplementedError
    @staticmethod
    def decide_scraper_class(portal_slug: str, content_source_to_refresh):
        if portal_slug == "ninegag":
            if content_source_to_refresh.source_name in ("top",):
                return NinegagGroupSource(content_source_to_refresh)
            return NinegagTagSource(content_source_to_refresh)
        if portal_slug == "youtube":
            return YoutubeVideoSource(content_source_to_refresh)

        raise NotImplementedError

    def _prohibit_refresh(self):

        if DEBUGGING:
            return False
        # TODO: TZ thing
        if self.content_source_to_refresh.last_checked_at and self.content_source_to_refresh.last_checked_at <= datetime.utcnow().replace(
                tzinfo=None) - timedelta(days=1):
            logger.warning("Refresh prohibited as the source was refreshed less than a X ago")
            return True
        return False

    def refresh(self, db: Session, ) -> None:
        # TODO: i freaking hate the creation and search of topics. Its dumb as fuck
        #  but i dunno how to do it better
        """

        :param db:
        :return:
        """

        if self._prohibit_refresh():
            return

        self.content_refresher.save(db)
        return



if __name__ == '__main__':
    with SessionLocalApp() as session:
        lala = session.query(SourceModel).where(SourceModel.id == 2).one()
        controller = ContentBridge(lala)
        controller.refresh(session)
    print()