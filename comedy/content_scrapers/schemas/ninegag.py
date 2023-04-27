from typing import Dict
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from content_scrapers.schemas.common import Image


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


class NinegagPhoto(NinegagBase):
    images: Dict[ImageSize, Image] = Field(alias="thumbnails")


class AnimatedImage(Image):
    duration: int


class NinegagAnimated(NinegagPhoto):
    images: Dict[AnimatedImageSize, AnimatedImage | Image] = Field(alias="thumbnails")
