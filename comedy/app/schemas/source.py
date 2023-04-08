from pydantic import BaseModel
from .content import Content

class SourceSimplified(BaseModel):
    id: int

class SourceUpdate(SourceSimplified):
    ...


class SourceBase(SourceSimplified):
    id: int
    source_id: str | None
    source_name: str

    class Config:
        orm_mode = True


class SourceFull(SourceBase):
    contents: None
