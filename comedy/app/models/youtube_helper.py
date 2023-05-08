from content_scrapers.schemas.common import Image, ImageNoSize
from pydantic.error_wrappers import ValidationError


class YoutubeMixin:
    @property
    def get_thumbnails(self, size: str | None = None) -> Image | ImageNoSize:
        if not size:
            thumbnail = self.thumbnails.get("default", {})
            if thumbnail:
                try:

                    return Image(**thumbnail)
                except ValidationError:
                    return ImageNoSize(**thumbnail)

        raise NotImplementedError
        return self.thumbnails.get("default", {})
