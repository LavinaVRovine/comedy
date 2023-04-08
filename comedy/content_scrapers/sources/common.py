from abc import ABC, abstractmethod
from dataclasses import dataclass


class ContentSource(ABC):

    @abstractmethod
    def get_content(self):
        raise NotImplementedError
@dataclass
class ReturnedContent:
    content: dict
    topics: set[str]