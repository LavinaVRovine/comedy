from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.content_source import Portal
from app.models.user_content import UserPortal, UserSource

from app.schemas.user_portal_and_source import UserSourceFull as UserSourceSchema, UserSourceUpdate

# TODO: not certain i like these Crud helpers. I mean its nice, but it gets fairly blackboxy
class CRUDUserSource(CRUDBase[UserSource, UserSourceSchema, UserSourceUpdate]):
    pass


user_source = CRUDUserSource(UserSource)
