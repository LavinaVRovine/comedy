from app.db.base_class import Base
from .content_source import ContentSource
from sqlalchemy import Column, INTEGER, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from datetime import datetime


class Content(Base):
    id = mapped_column(String(100), primary_key=True)
    title: Mapped[str]  # = Column(String(100))
    description: Mapped[str | None]  # = Column(String, nullable=True)
    published_at: Mapped[datetime]  # = Column(DateTime)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)

    source: Mapped["ContentSource"] = relationship(back_populates="contents")
    source_id = Column(INTEGER, ForeignKey("source.id"))
    __mapper_args__ = {'polymorphic_on': content_type}


class YoutubeVideo(Content):
    __mapper_args__ = {'polymorphic_identity': 'youtube_video'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)


class NinegagPost(Content):
    __tablename__ = "ninegag_post"
    __mapper_args__ = {'polymorphic_identity': 'ninegag_post'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnailz = Column(INTEGER)