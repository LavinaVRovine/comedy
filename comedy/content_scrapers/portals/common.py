from abc import ABC, abstractmethod
from content_scrapers.portals.connectors.common import Connector
from pydantic import BaseModel


class ContentPortal(ABC):

    def __init__(self,):
        self.content: dict[str, BaseModel] = {}
        self._connector: Connector = None

    @property
    def connector(self):
        if not self._connector:
            raise ValueError("Define connector")
        return self._connector

    @abstractmethod
    def get_content(self):
        raise NotImplementedError
