import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder
from app import models
from app.models.user import User
from app.models.content_source import Portal, ContentSource
from app.models.user_content import UserPortal, UserSource


from app.schemas.user_source import UserSourceFull as UserSourceSchema, UserSourceUpdate
from app.schemas import UserSourceFake
from app.crud.crud_user_portal import user_portal as user_portal_crud
from app.crud.crud_source import source as crud_source
from app import crud
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from content_scrapers.portals.common import ContentPortal


# noinspection PyMethodMayBeStatic
class CRUDUserSource(CRUDBase[UserSource, UserSourceSchema, UserSourceUpdate]):
    def create(self, db: Session, *, obj_in: UserSourceFake, user: models.User) -> models.UserSource:
        obj_in_data = jsonable_encoder(obj_in,exclude={"portal_slug": True})
        obj_in_data["source"] = crud.source.get(db, id=obj_in.source.id)
        obj_in_data["user_portal"] = obj_in.user_portal
        obj_in_data["user"] = user
        #obj_in["user_portal"] = user_portal
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        user_source_in.source = crud.source.get(db, id=user_source_in.source.id)
    def _sync_user_sources_with_syncable_portal(self, db: Session, *, user_portal: UserPortal, portal_connector: "ContentPortal"):
        """
        Get sources from portal that supports user specific sources inthere. FOr instance
        followed users in Youtuve
        :param db:
        :param user_portal:
        :param portal_connector:
        :return:
        """
        all_sources = portal_connector.save(db)
        user_sources = [us.source for us in user_portal.user_sources]
        new_user_sources = [UserSource(source=s, user_portal=user_portal,
                                       user=user_portal.user
                                       ) for s in all_sources if
                            s not in user_sources]
        if new_user_sources:
            db.add_all(new_user_sources)

            #db.commit()

            # db.refresh(user_portal)
        user_portal.last_remote_sync_at = datetime.datetime.utcnow()
        db.add(user_portal)
        db.commit()
        return user_sources + new_user_sources

    def _filter_already_created_user_sources(self, sources, user_portal: models.UserPortal):
        # TODO: i think it can be written in sql right away
        user_has_these_sources = [s.source for s in user_portal.user_sources]
        return [s for s in sources if s not in user_has_these_sources]

    def fake_recommended_user_sources(self, db: Session, *, user_portal: UserPortal)-> list[models.UserSource]:

        sources = crud_source.get_recommended_sources(db=db, portal=user_portal.portal)

        return self._create_fake_user_sources(
            sources=self._filter_already_created_user_sources(sources, user_portal), user_portal=user_portal
        )

    def fake_all_user_sources(self, db: Session, *, user_portal: models.UserPortal, include_followed: bool=True)-> list[models.UserSource]:

        sources = crud_source.get_multi(db, portal=user_portal.portal)
        return self._create_fake_user_sources(
            sources=self._filter_already_created_user_sources(sources, user_portal), user_portal=user_portal
        )

    def get_multi(
            self, db: Session, *, user_portal: models.UserPortal | None= None, skip: int = 0, limit: int = 100
    ) -> list[models.UserSource]:
        if user_portal:
            statement = select(self.model).join(models.UserPortal, self.model.user_portal_id == models.UserPortal.id).where(self.model.user_portal == user_portal).offset(skip).limit(limit)
            return db.execute(statement).scalars().all()
        return db.query(self.model).offset(skip).limit(limit).all()

    def _create_fake_user_sources(self, sources: list[models.ContentSource], user_portal: models.UserPortal) -> list[models.UserSource]:

        return [models.UserSource(source=cs, user_portal=user_portal, is_active=False, watching=False) for cs in sources]

    def _generate_user_sources_for_portal(self, db: Session, *, user_portal: UserPortal):
        """
        Get sources from portals like 9gag, where user specific sources are either not supported
        or not supported by me.
        :param db:
        :param user_portal:
        :return:
        """
        filtered_sources = select(models.ContentSource).where(
            models.ContentSource.portal_id == user_portal.portal_id).subquery()

        aliased_content_sources = aliased(models.ContentSource, filtered_sources, )

        statement = select(
            aliased_content_sources, models.UserSource
        ).outerjoin_from(
            aliased_content_sources, models.UserSource, aliased_content_sources.id == models.UserSource.source_id
        )
        lala = db.execute(
            statement
        ).all()
        all_user_sources = []
        for r in lala:
            cs: models.ContentSource = r[0]
            ucs: models.UserSource | None = r[1]
            if ucs is None:
                ucs = models.UserSource(source=cs, user_portal=user_portal, is_active=False, watching=False)

            all_user_sources.append(ucs)
        db.add_all(all_user_sources)
        db.add(user_portal)
        db.commit()
        return all_user_sources
    # def get_multi(
    #     self, db: Session, *, user_portal: UserPortal, skip: int = 0, limit: int = 100
    # ) -> list[UserSource]:
    #     statement = select(models.UserSource).where(UserPortal.portal == user_portal)
    #     user_sources = db.execute(statement).scalars().all()
    #     return user_sources

    def sync_user_sources_with_portal(self, db: Session, user: User, *,  user_portal: UserPortal) -> list[UserSource]:
        """
        Check what is being 'followed' in the portal, if something new -> add
        The already existing so far stay the same
        :param db:
        :param user:
        :return:
        """
        # TODO: CARE IAM REFRESHING PORTAL AND NOT CERTAIN I WANT THAT
        print("MISSING SOURCES? Maybe chekc hier")
        try:
            portal_something = ContentBridge.decide_portal_connector_class(user_portal.portal.slug)()
            return self._sync_user_sources_with_syncable_portal(db, user_portal=user_portal, portal_connector=portal_something)
        except NotImplementedError:
            return
            return self._generate_user_sources_for_portal(db, user_portal=user_portal)


user_source = CRUDUserSource(UserSource)





if __name__ == '__main__':
    from app.db.session import SessionLocalApp, engine
    session = SessionLocalApp()

    user = session.scalar(
        select(User).where(User.id == 1)
    )
    portal = session.scalar(
        select(
            models.Portal
        ).where(models.Portal.slug == "youtube")
    )
    user_portal = session.scalar(
        select(models.UserPortal)
    )
    user_source.get_multi(
        db=session, user_portal=user_portal
    )
    x = user_source.sync_user_sources_with_portal(
        session, user, portal_slug="youtube"
    )