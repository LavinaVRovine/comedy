from abc import ABC, abstractmethod
from content_scrapers.sources.connectors.common import Connector


class ContentSource(ABC):

    def __init__(self, source_name: str | None = None):

        self.raw_content = None
        self.content: dict[str, dict] = {}
        self._connector: Connector = None


    @property
    def connector(self):
        if not self._connector:
            raise ValueError("Define connector")
        return self._connector

    @abstractmethod
    def get_content(self):
        raise NotImplementedError