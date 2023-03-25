import logging

import sqlalchemy.exc
from sqlalchemy.orm import Session
from app.models.content_source import ContentSource as SourceModel
from content_scrapers.sources.common import ContentSource
from content_scrapers.sources.youtube import YoutubePlaylist
from app.db.session import SessionLocalApp, SessionLocalAppAsync
from datetime import datetime, timedelta
from comedy.config import DEBUGGING
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
        # TODO:
        if DEBUGGING:
            return False
        if self.content_source_to_refresh.last_checked_at and self.content_source_to_refresh.last_checked_at <= datetime.utcnow().replace(
                tzinfo=None) - timedelta(days=1):
            logger.warning("Refresh prohibited as the source was refreshed less than a X ago")
            return True
        return False

    def refresh(self, db: Session, since: datetime | None = None):
        # TODO: since not used. Its in the refresh thingy
        if self._prohibit_refresh():
            return
        to_add = self.content_refresher.get_content()

        try:
            db.bulk_save_objects(to_add)
            self.content_source_to_refresh.last_checked_at = datetime.utcnow().replace(tzinfo=None)

            db.commit()
            return
        except sqlalchemy.exc.IntegrityError as e:
            logger.warning(f"Attempted to add existing content. Skipping. {e}")


if __name__ == '__main__':
    with SessionLocalApp() as session:
        lala = session.query(SourceModel).where(SourceModel.id == 1).one()
        controller = ContentController(lala)
        controller.refresh(session)
    print()