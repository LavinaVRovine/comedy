from pydantic import BaseModel

from .user import User
from .content import Portal


class UserPortalBase(BaseModel):
    id: int
    portal: Portal
    watching: bool | None
    user: User

    class Config:
        orm_mode = True


class UserPortalGet(UserPortalBase):
    syncable: bool


class UserPortalCreate(UserPortalBase):
    id: int | None


class UserPortalUpdateWatching(BaseModel):
    watching: bool
