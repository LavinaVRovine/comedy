from typing import Any, Dict, Union

from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from app.crud.base import CRUDBase
from app import models

from app.schemas.user_portal import UserPortalCreate, UserPortalUpdateWatching


class CRUDUserPortal(CRUDBase[models.UserPortal, UserPortalCreate, UserPortalUpdateWatching]):

    # def create(self, db: Session, *, obj_in: UserPortalCreate) -> models.UserPortal:
    #
    #     db_obj = models.UserPortal(
    #
    #         watching=False,
    #         portal=obj_in.portal,
    #         user=obj_in.user,
    #
    #     )
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    def update(
            self, db: Session, *, db_obj: models.UserPortal, obj_in: Union[UserPortalUpdateWatching, Dict[str, Any]]

    ):
        return super(CRUDUserPortal, self).update(
            db, db_obj=db_obj, obj_in=obj_in
        )

    def _refresh_user_portal_sources(self, db: Session, user: models.User, *, user_portal : models.UserPortal, enforce_refresh: bool = False) -> models.UserPortal:
        """
        Sync
        :param db:
        :param user:
        :param user_portal:
        :param enforce_refresh:
        :return:
        """
        from .crud_user_source import user_source

        all_user_sources = user_source.sync_user_sources_with_portal(db, user, user_portal=user_portal)
        # TODO: prohibit nejakly casty refresh
        return user_portal

    def get_user_portal(self, db: Session, user: models.User, *, portal_slug: str, ) -> models.UserPortal:
        """
        gimme my setup
        :param db:
        :param user:
        :param portal_slug:
        :return:
        """
        user_portal_instance = db.query(models.UserPortal).filter(
            models.UserPortal.user_id == user.id,
            models.UserPortal.portal.has(
                models.Portal.slug == portal_slug,
            )
        ).first()
        return user_portal_instance

    def get_and_create_user_portals(self, db: Session, user: models.User, ) -> list[models.UserPortal]:
        """
        Get user portals
        Enforces that user has ALL available portals mapped to itself
        Pretty much when user accesses /portals, he gets his portals, ok
        Do i actually want to create them though?
        :param db:
        :param user:
        :return:
        """
        user_portal_subquery = select(models.UserPortal).join(models.User).where(models.User.id == user.id).subquery()
        us_aliased = aliased(models.UserPortal, user_portal_subquery, )
        final_statement = select(models.Portal, us_aliased).outerjoin_from(
            models.Portal, us_aliased, models.Portal.id == us_aliased.portal_id
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


user_portal = CRUDUserPortal(models.UserPortal)
