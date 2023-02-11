from typing import Optional
from dataclasses import dataclass

from content.content_models.common import Content


@dataclass
class YoutubeChanel(Content):

    title: str
    description: Optional[str] = None




