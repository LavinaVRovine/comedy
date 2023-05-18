from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from content_scrapers.schemas.common import Image


class Content(BaseModel):
    id: str
    title: str
    description: Optional[str]
    published_at: datetime
    # thumbnails: Image | None = Field(alias="get_thumbnails")
    duration: float
    get_thumbnails: Image | None
    get_image_content: Image | None
    # source: Source

    class Config:
        orm_mode = True
