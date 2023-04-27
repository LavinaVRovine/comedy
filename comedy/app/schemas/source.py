from pydantic import BaseModel
from .content import Content
from content_scrapers.schemas.common import ImageNoSize


class SourceSimplified(BaseModel):
    id: int


class SourceUpdate(SourceSimplified):
    ...


class SourceBase(SourceSimplified):
    id: int
    source_id: str | None
    source_name: str
    recommended: bool | None

    class Config:
        orm_mode = True


class SourceCreate(SourceBase):
    id: int = None
    source_id: str
    source_name: str
    portal_id: int


class SourceGet(SourceBase):
    get_thumbnails: ImageNoSize | None  # ImageNoSize


class SourceFull(SourceGet):
    contents: None
