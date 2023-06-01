from typing import cast
from content_scrapers.portals.common import ContentPortal
from content_scrapers.portals.connectors.youtube_connector import YoutubePortalConnector
from content_scrapers import schemas


class YoutubeUploadedPlaylist(ContentPortal):

    def __init__(self, connector=YoutubePortalConnector()):
        super(YoutubeUploadedPlaylist, self).__init__()
        self._connector = connector
        self.service = self.connector.service
        self.content = cast(dict[str, schemas.YoutubeUploadsPlaylist], self.content)

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

    # def _prepare_db_instance(self, obj: YoutubeUploadsPlaylist) -> dict:
    #     return {
    #         "target_system_id": obj.id, "source_name": obj.snippet.title,
    #         "description": obj.snippet.description,
    #         "thumbnails": {k: v.dict() for k, v in obj.snippet.thumbnails.items()},
    #         "portal": self.portal
    #     }

    # def _update_source_checked_datetime(self, db: Session):
    #     return

    # def save(self, db: Session, ):
    #     super(YoutubeUploadedPlaylist, self).save(db)
    #     if not self.portal:
    #         self.portal = self._get_my_db_portal(db)
    #     return self._save_new_content_instances_and_update(db=db)
    #     statement = select(ContentSourceModel).where(ContentSourceModel.source_id.in_(
    #         [s.id for s in self.content]
    #     ))
    #
    #     existing_sources = db.execute(
    #         statement
    #     ).scalars().all()
    #     existing_ids = [x.target_system_id for x in existing_sources]
    #     new_sources = [self._cast_to_db_instance(x) for x in self.content if
    #                    x.id not in existing_ids]
    #     if new_sources:
    #         db.add_all(new_sources)
    #         db.commit()
    #
    #     return existing_sources + new_sources

    def get_content(self) -> None:
        """
        Get current user subscriptions
        :return:
        """
        resource_ = self.service.subscriptions()

        content = {i:
            schemas.YoutubeUploadsPlaylist.parse_obj(
                self._add_uploads_playlist_id(x)) for i, x in enumerate(self.connector.fetch_list_items(
            resource_, "snippet", mine=True
        ))
        }
        self.content = content
        return None
