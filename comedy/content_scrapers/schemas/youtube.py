from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from .common import Image, ImageNoSize, Topic


class ImageSize(str, Enum):
    default = "default"
    medium = "medium"
    high = "high"
    standard = "standard"
    maxres = "maxres"


class ResourceId(BaseModel):
    video_id: str = Field(alias="videoId")


class Snippet(BaseModel):

    title: str
    description: str | None
    thumbnails: dict[ImageSize, Image] = Field(alias="thumbnails")

class VideoSnippet(Snippet):
    resource_id: ResourceId = Field(alias="resourceId")
class ContentDetails(BaseModel):
    duration: int


class TopicDetails(BaseModel):
    topic_categories: list[str] = Field(alias="topicCategories")
    class Config:
        allow_population_by_field_name = False

class YoutubeBase(BaseModel):
    id: str = Field(alias="target_system_id")
    kind: str

class YoutubeVideoBase(YoutubeBase):
    # ID is just an arbitrary ID returned. Video Id is in snippet
    id: str | None = Field(alias="target_system_id")
    snippet: VideoSnippet
    content_details: ContentDetails = Field(alias="contentDetails")
    published_at: datetime = Field(alias="publishedAt")
    # url: str

    description: str | None
    topic_details: TopicDetails | None = Field(alias="topicDetails", )
    #topicDetails: TopicDetails | None = Field(alias="topic_details")
    class Config:
        allow_population_by_field_name = True




class ChannelId(BaseModel):
    channelId: str = Field(alias="channel_id")
    class Config:
        allow_population_by_field_name = True
class SubscriptionSnippet(Snippet):
    # FIXME: inconsistency between these data fields. Should I specify string and then cast
    #  or should i first cast and specify datetime here?
    publishedAt: str = Field(alias="published_at")

    # channelId: str = Field(alias="channel_id") this is actually like MY? id
    resourceId: ChannelId = Field(alias="resource_id")
    thumbnails: dict[ImageSize, ImageNoSize] = Field(alias="thumbnails")
    class Config:
        allow_population_by_field_name = True


class YoutubeSubscriptionBase(YoutubeBase):
    snippet: SubscriptionSnippet

    class Config:
        allow_population_by_field_name = True


class YoutubeUploadsPlaylist(YoutubeSubscriptionBase):
    # FIXME: ok ja nicmene pak vydavam subscription za yt playlist coz je meeeh
    playlist_id: str
    id: str = Field(alias="target_system_id")
    class Config:
        allow_population_by_field_name = True