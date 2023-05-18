from typing import Dict
from enum import Enum
from datetime import datetime
from pydantic import Field, BaseModel

from content_scrapers.schemas.common import Image, Tag


class NinegagType(str, Enum):
    photo = "Photo"
    animated = "Animated"


class NinegagBase(BaseModel):
    id: str = Field(alias="target_system_id")
    # url: str
    title: str
    type: NinegagType
    description: str | None
    published_at: datetime
    tags: list[Tag] | None
    likes: int | None = Field(alias="upVoteCount")
    dislikes: int | None = Field(alias="downVoteCount")
    comments: int | None = Field(alias="commentsCount")

    class Config:
        allow_population_by_field_name = True
    # class Config:
    #     fields = {"target_system_id": "id"}


class ImageSize(str, Enum):
    image700 = "image700"
    image460 = "image460"
    imageFbThumbnail = "imageFbThumbnail"


class AnimatedImageSize(str, Enum):
    image700 = "image700"
    image460 = "image460"
    imageFbThumbnail = "imageFbThumbnail"
    image460sv = "image460sv"
    av1Url = "av1Url"
    vp9Url = "vp9Url"
    h265Url = "h265Url"


class NinegagPhoto(NinegagBase):
    images: Dict[ImageSize, Image] = Field(alias="images")


class AnimatedImage(Image):
    duration: int
    hasAudio: int | None

from typing import Union, Optional
class NinegagAnimated(NinegagPhoto):
    images: Dict[AnimatedImageSize | str, AnimatedImage | Image] = Field(alias="images")


    def get_duration(self) -> int | None:
        for i in self.images.values():
            try:
                return i.duration
            except AttributeError:
                pass
        return
