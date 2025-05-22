# libs/schema/youtube/analysis_schema.py
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


class SentimentBreakdown(BaseModel):
    positive: int
    neutral: int
    negative: int


class Sentiments(BaseModel):
    video: SentimentBreakdown
    creator: SentimentBreakdown
    topic: SentimentBreakdown


class PersonInsight(BaseModel):
    name: str
    sentiment: Dict[str, int]  # positive / neutral / negative %
    remarks: List[str] = []  # up-to-three short remarks
    
class DiscussionItem(BaseModel):
    name: str
    mentions: int
    sentiment: SentimentBreakdown


class AnalysisSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    comment_id: PyObjectId
    sentiments: Sentiments
    headline: str
    discussions: Dict[str, List[DiscussionItem]]  # video / topic / creator
    people: List[PersonInsight]
    other_insights: List[str] = []
    video_requests: List[str] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
