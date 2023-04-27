from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Portal, ContentSource as ContentSourceModel
from app import models
from app.models.content_source import YoutubeContentSource
from content_scrapers.schemas.youtube import YoutubeUploadsPlaylist
from content_scrapers.sources.common import ContentSource
from content_scrapers.sources.connectors.youtube_connector import YoutubePortalConnector


class YoutubeUploadedPlaylist(ContentSource):
    INSTANCE_DB_MODEL = YoutubeContentSource
    SCHEMA_EXCLUDE = {"kind": True}

    def __init__(self):
        # ehm totally unsure about that source. Its there so i do not have to worry about failing save
        super(YoutubeUploadedPlaylist, self).__init__(source=None)
        self._connector = YoutubePortalConnector()
        self.service = self.connector.service
        self.portal = None

    @staticmethod
    def _get_my_db_portal(db: Session, ) -> models.Portal:
        return db.execute(
            select(Portal).where(Portal.slug == "youtube")
        ).scalar()

    @staticmethod
    def replace_channel_id_with_uploads_playlist_id(id_: str):
        if not id_[1] == "C":
            return id_
        # Actually its the same ID just with different second character
        return id_[:1] + "U" + id_[2:]

    def _add_uploads_playlist_id(self, subscription_response_obj: dict) -> dict:
        playlist_id = self.replace_channel_id_with_uploads_playlist_id(
            subscription_response_obj["snippet"]["resourceId"]["channelId"])
        subscription_response_obj["playlist_id"] = playlist_id
        subscription_response_obj["id"] = playlist_id
        return subscription_response_obj

    def get_my_subscriptions(self):
        return self.get_content()

    def _prepare_db_instance(self, obj: YoutubeUploadsPlaylist) -> dict:
        return {
            "source_id": obj.id, "source_name": obj.snippet.title,
            "description": obj.snippet.description,
            "thumbnails": {k: v.dict() for k, v in obj.snippet.thumbnails.items()},
            "portal": self.portal
        }

    def _update_source_checked_datetime(self, db: Session):
        return

    def save(self, db: Session, ):
        super(YoutubeUploadedPlaylist, self).save(db)
        if not self.portal:
            self.portal = self._get_my_db_portal(db)
        return self._save_new_content_instances_and_update(db=db)
        statement = select(ContentSourceModel).where(ContentSourceModel.source_id.in_(
            [s.id for s in self.content]
        ))

        existing_sources = db.execute(
            statement
        ).scalars().all()
        existing_ids = [x.source_id for x in existing_sources]
        new_sources = [self._cast_to_db_instance(x) for x in self.content if
                       x.id not in existing_ids]
        if new_sources:
            db.add_all(new_sources)
            db.commit()

        return existing_sources + new_sources

    def get_content(self) -> None:
        """
        Get current user subscriptions
        :return:
        """
        resource_ = self.service.subscriptions()

        content = {i:
            YoutubeUploadsPlaylist.parse_obj(
                self._add_uploads_playlist_id(x)) for i, x in enumerate(self.connector.fetch_list_items(
            resource_, "snippet", mine=True
        ))
        }
        self.content = content
        return None
