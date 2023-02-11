from app.db.base_class import Base
from sqlalchemy import Column, INTEGER, String, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Portal(Base):
    __tablename__ = "portal"
    id = Column(INTEGER, primary_key=True)
    portal_name = Column(String(50))
    portal_url = Column(String(100), unique=True)
    sources = relationship("Source", back_populates="portal")


class Source(Base):
    __tablename__ = "source"
    id = Column(INTEGER, primary_key=True)
    source_id = Column(String(50), nullable=True)
    source_name = Column(String(100))
    contents = relationship("Content", back_populates="source")
    last_checked_at = Column(DateTime, nullable=True)

    portal_id = Column(INTEGER, ForeignKey("portal.id"))
    portal = relationship("Portal", back_populates="sources")
    __table_args__ = (UniqueConstraint("portal_id", "source_id", name="_portal_source_name_uc"), )
