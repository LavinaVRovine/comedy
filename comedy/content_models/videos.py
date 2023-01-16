from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from content_models.common import Content


@dataclass
class YoutubeVideo(Content):

    title: str
    description: str
    published_at: datetime
    thumbnails: dict





