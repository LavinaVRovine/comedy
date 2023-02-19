from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models import User, Portal, ContentSource


class UserPortal(Base):
    __tablename__ = "user_portal"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    portal_id = Column(Integer, ForeignKey('portal.id'))
    watching = Column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="user_portals")
    portal: Mapped["Portal"] = relationship(back_populates="user_portals"
        #viewonly=True
    )
    user_sources: Mapped[List["UserSource"]] = relationship(back_populates="user_portal")


class UserSource(Base):
    __tablename__ = "user_portal_source"
    id = Column(Integer, primary_key=True)
    watching = Column(Boolean, default=True)  # is following in the my app
    is_active = Column(Boolean, default=True)  # is actively followed in destination app, for instance YT
    user_portal_id = Column(Integer, ForeignKey('user_portal.id'))
    source_id = Column(Integer, ForeignKey('source.id'))
    user_portal: Mapped[UserPortal] = relationship(back_populates="user_sources")

    source: Mapped["ContentSource"] = relationship()
