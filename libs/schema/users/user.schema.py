from pydantic import BaseModel, EmailStr, Field
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


class ChannelEntry(BaseModel):
    channel_id: PyObjectId = Field(..., alias="channel_id")
    is_owner: bool

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    password_hash: Optional[str] = None
    google_id: Optional[str] = None
    channels: List[ChannelEntry] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
