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
    Column("topic_key", ForeignKey("topic.key"), primary_key=True),
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
    statistics: Mapped[list["ContentStatistics"] | None] = relationship()
    topics: Mapped[list["Topic"] | None] = relationship("Topic", back_populates="contents", secondary=content_topic)

    __mapper_args__ = {'polymorphic_on': content_type}
    __table_args__ = (UniqueConstraint("target_system_id", "source_id", name="_target_system_id_source_name_uc"),)

    @property
    @abc.abstractmethod
    def get_thumbnails(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def get_image_content(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def remote_link(self):
        return f"{self.REMOTE_LINK_PREFIX}{self.target_system_id}"


class YoutubeVideo(Content):
    REMOTE_LINK_PREFIX = "https://www.youtube.com/watch?v="
    __mapper_args__ = {'polymorphic_identity': 'youtube_video'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    images = Column(JSON)
    duration: Mapped[float] = mapped_column(Float)

    @property
    def get_thumbnails(self, size: str | None = None) -> Image:
        if not size:
            thumbnail = self.images.get("default", {})
            if thumbnail:
                return Image(**thumbnail)

        raise NotImplementedError
        return self.thumbnails.get("default", {})

    @property
    def get_image_content(self):
        return self.get_thumbnails


class Topic(Base):
    __tablename__ = "topic"

    key = Column(String, primary_key=True)
    contents: Mapped[list["Content"] | None] = relationship("Content", back_populates="topics", secondary=content_topic)
    info = Column(JSON, nullable=True)
    url: Mapped[str] = mapped_column(String(100), nullable=True, )


class NinegagThumbnailsMixin:
    REMOTE_LINK_PREFIX = f"https://9gag.com/gag/"

    @property
    def get_thumbnails(self, size: str | None = None) -> Image:
        if not size:
            thumbnail = self.images.get("image700", {})
            if thumbnail:
                return Image(**thumbnail)
        print()

    @property
    def get_image_content(self):
        return self.get_thumbnails


# did not figure out how to make a ninegag post and then subclass
class NinegagAnimated(NinegagThumbnailsMixin, Content, ):
    __tablename__ = "ninegag_animated"
    __mapper_args__ = {
        "polymorphic_identity": "ninegag_animated",
        #"concrete": True,
    }
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    images = Column(JSON)
    duration: Mapped[float] = mapped_column(Float, nullable=False, )


class NinegagPhoto(NinegagThumbnailsMixin, Content, ):
    __tablename__ = "ninegag_photo"
    __mapper_args__ = {
        "polymorphic_identity": "ninegag_photo",
        # "concrete": True,
    }
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    images = Column(JSON)
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=6.)


class ContentStatistics(Base):
    id = Column(Integer, primary_key=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    content: Mapped["Content"] = relationship(back_populates="statistics")
    content_id = Column(Integer, ForeignKey("content.id"))
    likes: Mapped[int | None]
    dislikes: Mapped[int | None]
    comments: Mapped[int | None]
