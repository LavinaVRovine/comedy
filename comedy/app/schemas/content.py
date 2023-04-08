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
    thumbnails: Optional[dict]
    get_duration: float|None
    # source: Source
    class Config:
        orm_mode = True

