
from app import models
from source_managers.source_manager_ninegag import SourceManagerNinegag


def init_manager_from_class(source: models.ContentSource | str, ) -> SourceManagerNinegag:
    if isinstance(source, models.NinegagContentSource):
        return SourceManagerNinegag(source=source)

    raise ValueError


@staticmethod
def decide_portal_connector_class(portal_slug: str):
    if portal_slug == "youtube":
        return YoutubeUploadedPlaylist

    raise NotImplementedError