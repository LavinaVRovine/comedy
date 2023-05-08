import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models import User, Portal, ContentSource, Content
from sqlalchemy.event import listens_for

from sqlalchemy.orm import Mapped, relationship, mapped_column


class UserPortal(Base):
    __tablename__ = "user_portal"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    portal_id = Column(Integer, ForeignKey('portal.id'))
    watching = Column(Boolean, default=False)
    last_remote_sync_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped["User"] = relationship(back_populates="user_portals")
    portal: Mapped["Portal"] = relationship(back_populates="user_portals"
                                            # viewonly=True
                                            )
    user_sources: Mapped[List["UserSource"]] = relationship(back_populates="user_portal")

    @property
    def syncable(self):
        if self.portal.syncable:
            if not self.last_remote_sync_at:
                # TODO :Refactor
                return True
            return (datetime.datetime.utcnow() - self.last_remote_sync_at) > datetime.timedelta(days=1)

        return False

class UserSource(Base):
    __tablename__ = "user_source"
    id = Column(Integer, primary_key=True)
    watching = Column(Boolean, default=True)  # is following in the my app
    is_active = Column(Boolean, default=True, )  # is actively followed in destination app, for instance YT
    user_portal_id = Column(Integer, ForeignKey('user_portal.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('source.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    user_portal: Mapped[UserPortal] = relationship(back_populates="user_sources")
    source: Mapped["ContentSource"] = relationship()
    user: Mapped["User"] = relationship()
    __table_args__ = (UniqueConstraint("user_portal_id", "source_id", name="_user_portal_source_name_uc"),)
# @listens_for(UserSource, "init")
# def on_user_source_init(target, args, kwargs):
#     print()
class UserContent(Base):
    __tablename__ = "user_content"
    id = Column(Integer, primary_key=True)
    seen = Column(Boolean, default=True)

    content_id = Column(Integer, ForeignKey('content.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    content: Mapped["Content"] = relationship()
    user: Mapped["User"] = relationship()
