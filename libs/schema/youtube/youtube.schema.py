# libs/schema/youtube/youtube.schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# ---------------------------------------------------------------------------#
# sub-objects (unchanged)                                                    #
# ---------------------------------------------------------------------------#
class Thumbnail(BaseModel):
    url: str
    width: int
    height: int


class Thumbnails(BaseModel):
    default: Thumbnail
    medium: Thumbnail
    high: Thumbnail


class Localized(BaseModel):
    title: str
    description: str


class Snippet(BaseModel):
    title: str
    description: str
    customUrl: Optional[str] = None
    publishedAt: str
    thumbnails: Thumbnails
    localized: Localized
    country: Optional[str] = None


class RelatedPlaylists(BaseModel):
    likes: Optional[str] = None
    uploads: str


class ContentDetails(BaseModel):
    relatedPlaylists: RelatedPlaylists


class Statistics(BaseModel):
    viewCount: int
    subscriberCount: int
    hiddenSubscriberCount: bool
    videoCount: int


# ---------------------------------------------------------------------------#
# channel                                                                    #
# ---------------------------------------------------------------------------#
class ChannelSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    youtube_channel_id: str

    kind: str
    etag: str
    snippet: Snippet
    contentDetails: ContentDetails
    statistics: Statistics

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ---------------------------------------------------------------------------#
# video                                                                      #
# ---------------------------------------------------------------------------#
class VideoSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    youtube_video_id: str
    channel_id: PyObjectId  # Mongo _id of the channel
    publish_time: str
    view_count: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None  # ISO 8601 (e.g. PT6M5S)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ---------------------------------------------------------------------------#
# comments                                                                   #
# ---------------------------------------------------------------------------#
class CommentSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: PyObjectId
    comments: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
