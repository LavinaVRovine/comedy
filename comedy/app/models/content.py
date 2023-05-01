import abc
from content_scrapers.schemas.common import Image
from app.db.base_class import Base
from .content_source import ContentSource
from sqlalchemy import Column, INTEGER,Integer, String, DateTime, JSON, ForeignKey, Table, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column
from datetime import datetime


content_topic = Table(
    "content_topic",
    Base.metadata,
    Column("content_id", ForeignKey("content.id"), primary_key=True),
    Column("topic_id", ForeignKey("topic.id"), primary_key=True),
)
class Content(Base):
    id = Column(INTEGER, primary_key=True)
    target_system_id = mapped_column(String(100), primary_key=False,)
    title: Mapped[str]  # = Column(String(100))
    description: Mapped[str | None]  # = Column(String, nullable=True)
    published_at: Mapped[datetime]  # = Column(DateTime)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped["ContentSource"] = relationship(back_populates="contents")
    source_id = Column(INTEGER, ForeignKey("source.id"))

    topics: Mapped[list["Content"] | None] = relationship("Topic", back_populates="contents", secondary=content_topic)

    __mapper_args__ = {'polymorphic_on': content_type}
    __table_args__ = (UniqueConstraint("target_system_id", "source_id", name="_target_system_id_source_name_uc"),)

    @property
    @abc.abstractmethod
    def get_thumbnails(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def get_duration(self):
        raise NotImplementedError


class YoutubeVideo(Content):
    __mapper_args__ = {'polymorphic_identity': 'youtube_video'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)
    duration: Mapped[float] = mapped_column(Float)

    @property
    def get_thumbnails(self, size: str | None = None) -> Image:
        if not size:
            thumbnail = self.thumbnails.get("default", {})
            if thumbnail:
                return Image(**thumbnail)

        raise NotImplementedError
        return self.thumbnails.get("default", {})

    @property
    def get_duration(self):
        return self.duration


class Topic(Base):
    id = Column(INTEGER, primary_key=True)
    wiki_link: Mapped[str] = mapped_column(String(100), unique=True, )
    contents: Mapped[list["Content"] | None] = relationship("Content", back_populates="topics", secondary=content_topic)

class NinegagThumbnailsMixin:
    @property
    def get_thumbnails(self, size: str | None = None) -> Image:
        if not size:
            thumbnail = self.thumbnails.get("image700", {})
            if thumbnail:
                return Image(**thumbnail)
        print()
# did not figure out how to make a ninegag post and then subclass
class NinegagAnimated(NinegagThumbnailsMixin,Content, ):
    __tablename__ = "ninegag_animated"
    __mapper_args__ = {
        "polymorphic_identity": "ninegag_animated",
        #"concrete": True,
    }
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)
    duration: Mapped[float] = mapped_column(Float, nullable=True)
    @property
    def get_duration(self):
        return self.duration if self.duration else 6.

class NinegagPhoto(NinegagThumbnailsMixin,Content, ):
    __tablename__ = "ninegag_photo"
    __mapper_args__ = {
        "polymorphic_identity": "ninegag_photo",
        #"concrete": True,
    }
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)

    @property
    def get_duration(self):
        return 6.
