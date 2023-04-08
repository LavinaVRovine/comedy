import datetime

from pydantic import BaseModel

from .source import SourceBase
from .user import User
from .content import Portal

class UserPortalBase(BaseModel):
    id: int
    portal: Portal
    watching: bool | None
    user: User

    class Config:
        orm_mode = True


class UserPortalCreate(UserPortalBase):
    ...
class UserPortalUpdate(BaseModel):

    watching: bool


# TODO: not sure about this inheritance
class UserSourceBase(BaseModel):
    id: int
    watching: bool | None
    is_active: bool | None
    # source: SourceBase
    #last_checked_at: datetime.datetime | None

    class Config:
        orm_mode = True

class UserSourceFull(UserSourceBase):
    source: SourceBase
class UserSourceCreate(UserSourceBase):
    pass


class UserSourceUpdate(BaseModel):
    # not inheriting as i do not want to send ID
    # id = None
    watching: bool


class UserPortalFull(UserPortalBase):
    user_sources: list[UserSourceFull]
