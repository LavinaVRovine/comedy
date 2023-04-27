from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from content_scrapers.schemas.common import Image

class PortalBase(BaseModel):
    name: str

class Portal(PortalBase):
    id: int
    name: str
    get_thumbnails: str
    get_url_slug: str
    class Config:
        orm_mode = True


class Content(BaseModel):
    id: str
    title: str
    description: Optional[str]
    published_at: datetime
    #thumbnails: Image | None = Field(alias="get_thumbnails")
    get_duration: float|None
    get_thumbnails: Image | None
    # source: Source
    class Config:
        orm_mode = True

