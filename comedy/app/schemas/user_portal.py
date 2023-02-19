import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from . import Portal
from .user import User
from .content import Portal

# Shared properties
# FIXMe: tohle bylo jeste nez byl user portal takze adjust
class UserPortalBaseDEPRECATED(Portal):
    is_following: bool | None

    class Config:
        orm_mode = False



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


class SourceBase(BaseModel):
    id: int
    source_id: str | None
    source_name: str

    class Config:
        orm_mode = True

class SourceFull(SourceBase):
    contents: None


class UserSource(BaseModel):
    id: int
    watching: bool
    is_active: bool
    source: SourceBase
    last_checked_at: datetime.datetime | None

    class Config:
        orm_mode = True


class UserPortalFull(UserPortalBase):
    user_sources: list[UserSource]
