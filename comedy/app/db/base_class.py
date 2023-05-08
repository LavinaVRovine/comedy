from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(
    #MappedAsDataclass,
    DeclarativeBase
):
    """"""
    # __name__: str
    # id: Any

    # Generate __tablename__ automatically
    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # FIXME: this is probably a really bad idea...I think i should just
        #  write the damn table names...
        try:
            return cls.__tablename__.lower()
        except RecursionError:
            return cls.__name__.lower()
