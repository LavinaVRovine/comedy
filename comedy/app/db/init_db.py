from sqlalchemy.orm import Session

from app import crud, schemas
from app import models
from app.core.config import settings
from app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28
from content_scrapers.refresh import refresh_portal
from app.schemas.source import SourceCreate
from source_managers import init_manager_from_class
from app.supported_portals import SupportedPortals


def init_db(db: Session, engine=None) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    base.Base.metadata.drop_all(bind=engine,)# tables={k:v for k, v in base.Base.metadata.tables.items() if k != "user"})
    base.Base.metadata.create_all(bind=engine)



    db.add(SupportedPortals.youtube)
    db.add(SupportedPortals.ninegag)

    top_source = crud.source.create(db, obj_in=SourceCreate(target_system_id="top", source_name="top", portal_id=p2.id, recommended=True))

    manager = init_manager_from_class(top_source)
    manager.refresh(db)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841
        # TODO: add this followed portals
        schemas.UserUpdate()

        u_p = models.UserPortal(
            user=user,
            portal=SupportedPortals.youtube,

        )
        user_portal_ninegag = models.UserPortal(
            user=user,
            portal=SupportedPortals.ninegag,

        )
        u_s = models.UserSource(
            watching=True,
            is_active=True,
            user_portal=user_portal_ninegag,
            source=top_source,
            user=user,
        )
        db.add(u_p)
        db.add(u_s)
        db.commit()


        crud.user_source.sync_user_sources_with_portal(db=db, user=user,user_portal=u_p )


    refresh_portal(2)
    refresh_portal(1)

    seen_content = models.UserContent(
            content_id=1,
            user=user
        )

    db.add(seen_content)

    db.commit()
