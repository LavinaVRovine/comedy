from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from app.models import Portal, ContentSource
from app.models.content_source import YoutubeContentSource
from app.models.user_content import UserPortal, UserSource, UserContent
# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28
from content_scrapers.content_controller import ContentBridge
from content_scrapers.refresh import refresh_portal
from app.schemas.source import SourceCreate


def init_db(db: Session, engine=None) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    base.Base.metadata.drop_all(bind=engine,)# tables={k:v for k, v in base.Base.metadata.tables.items() if k != "user"})
    base.Base.metadata.create_all(bind=engine)

    p = Portal(
        id=1, name="Youtube", url="whatever", img_path="youtube.png", remote_syncable=True
    )

    p2 = Portal(
        id=2, name="Ninegag", url="whatever2", img_path="9gag.png"
    )

    db.add(p)
    db.add(p2)

    top_source = crud.source.create(db, obj_in=SourceCreate(source_id="top", source_name="top", portal_id=p2.id, recommended=True))

    ContentBridge(content_source_to_refresh=top_source).refresh(db)

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

        u_p = UserPortal(
            user=user,
            portal=p,

        )
        user_portal_ninegag = UserPortal(
            user=user,
            portal=p2,

        )
        u_s = UserSource(
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

    seen_content = UserContent(
            content_id=1,
            user=user
        )

    db.add(seen_content)

    db.commit()
    print()