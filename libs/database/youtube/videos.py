from typing import Dict, List
from config.database import db
from bson import ObjectId


async def create_video(
    name: str,
    youtube_video_id: str,
    channel_id: str,
    publish_time: str,
    view_count: int,
):
    result = await db.videos.insert_one(
        {
            "name": name,
            "youtube_video_id": youtube_video_id,
            "channel_id": ObjectId(channel_id),
            "publish_time": publish_time,
            "view_count": view_count,
        }
    )
    return str(result.inserted_id)


async def create_videos(videos: List[Dict]) -> List[str]:
    """
    Bulk-insert a list of video dicts (already validated / shaped).
    Returns list[str] of inserted _id values.
    """
    result = await db.videos.insert_many(
        [
            {
                "name": v["name"],
                "description": v.get("description"),
                "youtube_video_id": v["youtube_video_id"],
                "channel_id": ObjectId(v["channel_id"]),
                "publish_time": v["publish_time"],
                "view_count": v["view_count"],
                "like_count": v.get("like_count"),
                "comment_count": v.get("comment_count"),
                "duration": v.get("duration"),
            }
            for v in videos
        ]
    )
    return [str(_id) for _id in result.inserted_ids]


async def get_videos_by_channel_id(channel_id: str):
    cursor = db.videos.find({"channel_id": ObjectId(channel_id)})
    return [video async for video in cursor]


async def get_video_by_id(video_id: str) -> Dict | None:
    v = await db.videos.find_one({"_id": ObjectId(video_id)})
    if not v:
        return None
    # flatten & stringify for callers
    return {
        "id": str(v["_id"]),
        "name": v.get("name"),
        "description": v.get("description"),
        "youtube_video_id": v.get("youtube_video_id"),
        "channel_id": str(v.get("channel_id")),
        "publish_time": v.get("publish_time"),
        "view_count": v.get("view_count"),
        "like_count": v.get("like_count"),
        "comment_count": v.get("comment_count"),
        "duration": v.get("duration"),
    }


async def get_videos_by_ids(video_ids: List[str]) -> List[dict]:
    ids = [ObjectId(vid) for vid in video_ids]
    cursor = db.videos.find({"_id": {"$in": ids}})
    return [
        {
            "id": str(v["_id"]),
            "name": v.get("name"),
            "publish_time": v.get("publish_time"),
            "channel_id": str(v.get("channel_id")),
        }
        async for v in cursor
    ]
