from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.content_source import Portal
from app.models.user_content import UserPortal

from app.schemas.user_portal_and_source import UserPortalCreate, UserPortalUpdate

# TODO: not certain i like these Crud helpers. I mean its nice, but it gets fairly blackboxy
class CRUDUserPortal(CRUDBase[UserPortal, UserPortalCreate, UserPortalUpdate]):

    def get_or_create_user_portal(self, db: Session, user: User, *, portal_slug: str) -> UserPortal:
        user_portal_instance = db.query(UserPortal).filter(
            UserPortal.user_id == user.id,
            UserPortal.portal.has(
                Portal.slug == portal_slug,
            )
        ).first()
        if user_portal_instance:
            return user_portal_instance
        portal = db.query(Portal).filter(Portal.slug == portal_slug).first()
        if not portal:
            # TODO write
            raise ValueError
        # noinspection PyTypeChecker
        return self.create(
            db=db, obj_in=type('UserPortalCreate', (), dict(user=user, portal=portal))
        )

    def get_and_create_user_portals(self, db: Session, user: User, ) -> list[UserPortal]:
        """
        Get user portals
        Enforces that user has ALL available portals mapped to itself
        :param db:
        :param user:
        :return:
        """
        user_portal_subquery = select(UserPortal).join(User).where(User.id == user.id).subquery()
        us_aliased = aliased(UserPortal, user_portal_subquery, )
        final_statement = select(Portal, us_aliased).outerjoin_from(
            Portal, us_aliased, Portal.id == us_aliased.portal_id
        )
        portals_and_user_portals = db.execute(
            final_statement
        ).all()
        out = []
        for res in portals_and_user_portals:
            up = res[1]
            if up is None:
                up = self.create(
                    db=db, obj_in=type('UserPortalCreate', (), dict(user=user, portal=res[0]))
                )
            out.append(
                up
            )

        return out

    def get(self, db: Session, id: Any):
        return super(CRUDUserPortal, self).get(db, id)
    def create(self, db: Session, *, obj_in: UserPortalCreate) -> UserPortal:
        db_obj = UserPortal(

            watching=False,
            portal=obj_in.portal,
            user=obj_in.user,

        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *, db_obj: UserPortal, obj_in: Union[UserPortalUpdate, Dict[str, Any]]

    ):
        return super(CRUDUserPortal, self).update(
            db, db_obj=db_obj, obj_in=obj_in
        )
        raise NotImplementedError
    def remove(self):
        raise NotImplementedError


user_portal = CRUDUserPortal(UserPortal)
