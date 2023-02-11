from abc import ABC, abstractmethod


class ContentSource(ABC):

    @abstractmethod
    def get_content(self):
        raise NotImplementedError
