from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .content import Content
    from .user import User
    from .user_content import UserPortal

from sqlalchemy import INTEGER, String, DateTime, ForeignKey, UniqueConstraint, JSON
from datetime import datetime
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from slugify import slugify
from app.db.base_class import Base


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
    thumbnail: Mapped[dict] = mapped_column(JSON)
    sources: Mapped[list["ContentSource"]] = relationship(
        #back_populates="portal"
    )
    user_portals: Mapped[list["UserPortal"]] = relationship(back_populates="portal")
    users: Mapped[list["User"]] = relationship(viewonly=True, secondary="user_portal",)# back_populates="followed_portals")

    @property
    def get_thumbnail(self):
        # TODO: atm no pics in DB
        return self.thumbnail["small"]

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
    source_id: Mapped[str] = mapped_column(String(50), nullable=True)
    source_name: Mapped[str] = mapped_column(String(100))
    contents: Mapped[list["Content"]] = relationship("Content", back_populates="source")
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    portal_id = mapped_column(INTEGER, ForeignKey("portal.id"))
    portal: Mapped[Portal] = relationship(back_populates="sources")
    __table_args__ = (UniqueConstraint("portal_id", "source_id", name="_portal_source_name_uc"), )

    # users: Mapped[list["User"]] = relationship(secondary="user_source", back_populates="followed_sources")
