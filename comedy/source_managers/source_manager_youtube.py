from source_managers.source_manager import SourceManager
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models
from content_scrapers.portals.common import ContentPortal
from content_scrapers.portals.youtube.youtube_playlist import YoutubeUploadedPlaylist


class SourceManagerYoutube(SourceManager):
    pass


class SourceManagerYoutubePlaylist(SourceManagerYoutube):

    def _update_source_checked_datetime(self, db: Session):
        return


    def save(self, *, source_scraper: YoutubeUploadedPlaylist, db: Session, **kwargs) -> list[models.ContentSource]:
        statement = select(models.ContentSource).where(models.ContentSource.source_id.in_(
            [s.id for s in source_scraper.content]
        ))

        existing_sources = db.execute(
            statement
        ).scalars().all()
        existing_ids = [x.target_system_id for x in existing_sources]
        tady
        new_sources = [x.cast_to_db_instance() for x in source_scraper.content if
                       x.id not in existing_ids]
        if new_sources:
            db.add_all(new_sources)
            db.commit()

        return existing_sources + new_sources

