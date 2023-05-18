from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# ENGINE = create_engine("postgresql+psycopg2://postgres:postgres@localhost/comedy")
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, connect_args={"options": "-c timezone=utc"})
SessionLocalApp = sessionmaker(engine, )
#async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI_ASYNC, echo=True, )
#SessionLocalAppAsync = async_sessionmaker(async_engine, expire_on_commit=False)
