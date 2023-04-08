import abc
import dataclasses

from app.db.base_class import Base
from .content_source import ContentSource
from sqlalchemy import Column, INTEGER, String, DateTime, JSON, ForeignKey, Table, Float
from sqlalchemy.orm import Mapped, relationship, mapped_column
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


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

    @property
    @abc.abstractmethod
    def get_thumbnails(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def get_duration(self):
        raise NotImplementedError


@dataclasses.dataclass
class Thumbnails:
    url: str
    width: int
    height: int


class YoutubeVideo(Content):
    __mapper_args__ = {'polymorphic_identity': 'youtube_video'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)
    duration: Mapped[float] = mapped_column(Float)

    def get_thumbnails(self, size:str|None = None) -> Thumbnails:
        if not size:
            thumbnail = self.thumbnails.get("default", {})
            if thumbnail:
                return Thumbnails(**thumbnail)

        raise NotImplementedError
        return self.thumbnails.get("default", {})

    @property
    def get_duration(self):
        return self.duration

class Topic(Base):
    id = Column(INTEGER, primary_key=True)
    wiki_link: Mapped[str] = mapped_column(String(100), unique=True, )
    contents: Mapped[list["Content"] | None] = relationship("Content", back_populates="topics", secondary=content_topic)


class NinegagPost(Content):
    __tablename__ = "ninegag_post"
    __mapper_args__ = {'polymorphic_identity': 'ninegag_post'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnailz = Column(INTEGER)
