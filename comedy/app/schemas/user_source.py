from pydantic import BaseModel

from app.schemas import UserPortalBase
from app.schemas.source import SourceGet, SourceBase


class UserSourceBase(BaseModel):
    id: int
    watching: bool | None
    is_active: bool | None
    # source: SourceBase
    #last_checked_at: datetime.datetime | None

    class Config:
        orm_mode = True


class UserSourceFull(UserSourceBase):
    source: SourceGet


class UserSourceUpdate(BaseModel):
    # not inheriting as i do not want to send ID
    # id = None
    watching: bool


class UserSourceFake(UserSourceFull):
    id: int | None
    portal_slug: str | None
    user_portal: UserPortalBase | None
