from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Source(BaseModel):
    ...


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