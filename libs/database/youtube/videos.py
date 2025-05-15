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


async def create_videos(videos: list):
    result = await db.videos.insert_many(
        [
            {
                "name": video["name"],
                "youtube_video_id": video["youtube_video_id"],
                "channel_id": ObjectId(video["channel_id"]),
                "publish_time": video["publish_time"],
                "view_count": video["view_count"],
            }
            for video in videos
        ]
    )
    return [str(video_id) for video_id in result.inserted_ids]


async def get_videos_by_channel_id(channel_id: str):
    cursor = db.videos.find({"channel_id": ObjectId(channel_id)})
    return [video async for video in cursor]


async def get_video_by_id(video_id: str):
    video = await db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        return None
    return {
        "id": str(video["_id"]),
        "name": video.get("name"),
        "youtube_video_id": video.get("youtube_video_id"),
        "channel_id": str(video.get("channel_id")),
        "publish_time": video.get("publish_time"),
        "view_count": video.get("view_count"),
    }
