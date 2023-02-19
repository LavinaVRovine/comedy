from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from app.models import Portal, ContentSource
from app.models.user_content import UserPortal, UserSource
# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session, engine=None) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    base.Base.metadata.drop_all(bind=engine,)# tables={k:v for k, v in base.Base.metadata.tables.items() if k != "user"})
    base.Base.metadata.create_all(bind=engine)

    p = Portal(
        id=1, name="Youtube", url="whatever", thumbnail={"small":"whatever"}
    )
    p2 = Portal(
        id=2, name="fake", url="whatever2", thumbnail={"small": "whatever"}
    )
    bs_source = ContentSource(
        source_id="UU4tWW-toq9KKo-HL3S8D23A",
        source_name="bittersteel_playlist",
        portal=p
    )
    db.add(p)
    db.add(p2)
    db.add(bs_source)
    #db.commit()

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
        u_s = UserSource(
            watching=True,
            is_active=True,
            user_portal=u_p,
            source=bs_source,
        )
        db.add(u_p)
        db.add(u_s)
        db.commit()