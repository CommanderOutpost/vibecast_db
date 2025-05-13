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


class ChannelSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    youtube_channel_id: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class VideoSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    youtube_video_id: str
    channel_id: PyObjectId  # refers to Mongo _id of the channel

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CommentSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    video_id: PyObjectId  # refers to Mongo _id of the video
    comments: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
