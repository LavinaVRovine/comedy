from app.db.base_class import Base
from .source import Source
from sqlalchemy import Column, INTEGER, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Content(Base):
    #__abstract__ = True
    __tablename__ = "content"
    id = mapped_column(String(100), primary_key=True)
    title: Mapped[str]# = Column(String(100))
    description = Column(String, nullable=True)
    published_at = Column(DateTime)
    content_type = Column(String(32), nullable=False)
    source = relationship("Source", back_populates="contents")
    source_id = Column(INTEGER, ForeignKey("source.id"))
    __mapper_args__ = {'polymorphic_on': content_type}


class YoutubeVideo(Content):
    __tablename__ = "youtube_video"
    __mapper_args__ = {'polymorphic_identity': 'youtube_video'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnails = Column(JSON)


class NinegagPost(Content):
    __tablename__ = "ninegag_post"
    __mapper_args__ = {'polymorphic_identity': 'ninegag_post'}
    id = Column(None, ForeignKey('content.id'), primary_key=True)
    thumbnailz = Column(INTEGER)