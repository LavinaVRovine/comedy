from pydantic import BaseModel, Field
from datetime import datetime
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
    last_remote_sync_at: datetime| None #= Field(default=datetime.utcnow())


class UserPortalCreate(UserPortalBase):
    id: int | None


class UserPortalUpdateWatching(BaseModel):
    watching: bool
