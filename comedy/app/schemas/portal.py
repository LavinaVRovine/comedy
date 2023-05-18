from pydantic import BaseModel


class PortalBase(BaseModel):
    name: str


class Portal(PortalBase):
    id: int
    name: str
    get_thumbnails: str
    get_url_slug: str
    syncable: bool

    class Config:
        orm_mode = True
