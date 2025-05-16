# libs/schema/youtube/analysis.schema.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
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


class AnalysisSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    comment_id: PyObjectId
    sentiments: Optional[Dict[str, Optional[int]]]  # may be None if missing
    major_discussions: Dict[
        str, List[str]
    ]  # always includes keys video, topic, creator
    other_insights: List[str]
    video_requests: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
