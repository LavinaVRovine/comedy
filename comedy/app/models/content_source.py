from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .content import Content
    from .user import User
    from .user_content import UserPortal

from sqlalchemy import INTEGER, String, Column, DateTime, ForeignKey, UniqueConstraint, JSON, Boolean
from datetime import datetime
from sqlalchemy.orm import Mapped, relationship, mapped_column
# noinspection PyPackageRequirements
from slugify import slugify
from app.db.base_class import Base
from content_scrapers.schemas.common import Image, ImageNoSize
from .youtube_helper import YoutubeMixin
def sluggify_name(context):
    return slugify(
        context.get_current_parameters()["name"]
    )


class Portal(Base):
    __tablename__ = "portal"
    """
    For instance YT, 9gag, redit etc
    """
    id = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(50), default=sluggify_name, onupdate=sluggify_name)
    url: Mapped[str] = mapped_column(String(100), unique=True)
    syncable: Mapped[bool] = mapped_column(Boolean, default=False, )
    img_path: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    sources: Mapped[list["ContentSource"]] = relationship(
        #back_populates="portal"
    )
    user_portals: Mapped[list["UserPortal"]] = relationship(back_populates="portal")
    users: Mapped[list["User"]] = relationship(viewonly=True, secondary="user_portal",)# back_populates="followed_portals")

    @property
    def get_thumbnails(self):
        if self.img_path:
            # FIXME
            print("HARDCODED URL!!!")
            return 'http://127.0.0.1:8000/static/' + self.img_path
        return ""

    @property
    def get_url_slug(self):
        return f"/{self.slug}"
    # @hybrid_property
    # def active_for_user(self, user: "User"):
    #     return self.users


class ContentSource(Base):
    __tablename__ = "source"
    """
    Could be a channel, subredit, nothing
    """
    id = mapped_column(INTEGER, primary_key=True)
    target_system_id: Mapped[str] = mapped_column(String(50), nullable=False, )
    source_name: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(32), nullable=True)
    contents: Mapped[list["Content"]] = relationship("Content", back_populates="source")
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    portal_id = mapped_column(INTEGER, ForeignKey("portal.id"))
    portal: Mapped[Portal] = relationship(back_populates="sources")
    #thumbnails = Column(JSON, nullable=True)
    __table_args__ = (UniqueConstraint("portal_id", "target_system_id", name="_portal_source_name_uc"), )

    __mapper_args__ = {'polymorphic_on': source_type, "polymorphic_identity": "source"}
    # users: Mapped[list["User"]] = relationship(secondary="user_source", back_populates="followed_sources")
    @property
    def remote_link(self) -> str:
        return
    def __repr__(self):
        return f"<Content Source>: {self.target_system_id}"

    @property
    def get_thumbnails(self, size: str | None = None) -> ImageNoSize | None:
        return None
        return ImageNoSize(url="")

class YoutubeContentSource(YoutubeMixin, ContentSource, ):
    __tablename__ = "youtube_playlist_source"
    __mapper_args__ = {'polymorphic_identity': 'youtube_playlist'}
    id = Column(None, ForeignKey('source.id'), primary_key=True)
    description: Mapped[str] = mapped_column(String(6400), nullable=True)
    images = Column(JSON)
    #portal: Mapped[Portal] = relationship(back_populates="sources", )


class NinegagContentSource(ContentSource):
    __tablename__ = "ninegag_source"
    __mapper_args__ = {'polymorphic_identity': 'ninegag_tag'}
    id = Column(None, ForeignKey('source.id'), primary_key=True)

    @property
    def get_thumbnails(self, size: str | None = None) -> ImageNoSize | None:
        return None
        return ImageNoSize(url="")