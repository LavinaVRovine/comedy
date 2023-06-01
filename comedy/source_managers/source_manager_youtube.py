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

class SourceManagerVideoYoutube(SourceManagerYoutube):
    SCHEMA_EXCLUDE = {"kind": True, "topic_details": True, }

    def _prepare_db_instance(self, obj) -> dict:
        as_dict = obj.dict(by_alias=False, exclude=self.SCHEMA_EXCLUDE)
        as_dict["source"] = self.source
        as_dict.pop("id")
        as_dict["target_system_id"] = as_dict["snippet"]["resource_id"]["video_id"]
        as_dict = as_dict | as_dict.pop("snippet")
        as_dict = as_dict | as_dict.pop("content_details")
        as_dict.pop("resource_id")
        return as_dict

    def _save_new_content_instances_and_update(self, db: Session, ):
        videos = []
        for k, v in self.content.items():
            vid = self._cast_to_db_instance(v)
            try:
                this_vid_topics = filter(lambda x: x.url in [t for t in v.topic_details.topic_categories],
                                     self.topics_as_db_instances)
                vid.topics = list(this_vid_topics)
            except AttributeError:
                pass
            finally:
                videos.append(vid)

        try:
            db.add_all(videos)
            # TODO: how about we switch to NEWEST content DT rather than refresh date?
            self.source.last_checked_at = max(
                [m.published_at for m in videos])  # datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)
            db.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # there is an implicit assumption in refresh, that we are refreshing only new videos?
            # but theoretically something might go wrong?
            db.rollback()
            existing_titles = [x.title for x in self.source.contents]
            to_add = [x for x in videos if x.title not in existing_titles]
            if not to_add:
                return to_add
            db.add_all(to_add)
            self.source.last_checked_at = max(
                [m.published_at for m in to_add])  # datetime.utcnow().astimezone(tz=pytz.UTC)#.replace(tzinfo=None)

    def save(self, db: Session, ):
        if not self.content:
            self.get_content()
        self._save_set_topics(db)
        super(YoutubeVideoPortal, self).save(db)