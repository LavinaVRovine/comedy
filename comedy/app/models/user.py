
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from .content_source import Portal, ContentSource
from .user_content import UserPortal, UserSource


class User(Base):
    __tablename__ = "user"
    id = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)

    user_portals: Mapped[list[UserPortal]] = relationship(foreign_keys="UserPortal.user_id", back_populates="user")

    # followed_portals: Mapped[list[Portal]] = relationship(viewonly=True, secondary=UserPortal.__table__, )# back_populates="users")

    user_sources: Mapped[list[UserSource]] = relationship(viewonly=True, secondary=UserPortal.__table__, )# back_populates="users")
