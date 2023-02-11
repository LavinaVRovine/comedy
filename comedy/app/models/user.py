from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.base_class import Base


class User(Base):
    id = mapped_column(Integer, primary_key=True)
    #id = Column(Integer, primary_key=True, index=True)
    full_name = mapped_column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = mapped_column(String, nullable=False) #Mapped[str] #Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

