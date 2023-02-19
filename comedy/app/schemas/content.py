from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Portal(BaseModel):
    id: int
    name: str
    get_thumbnail: str
    get_url_slug: str
    class Config:
        orm_mode = True


class Content(BaseModel):
    id: str
    title: str
    description: Optional[str]
    published_at: datetime
    # source: Source
    class Config:
        orm_mode = True

class YoutubeVideo(Content):
    thumbnails: Optional[dict]

class NinegagPost(Content):
    thumbnailz: int