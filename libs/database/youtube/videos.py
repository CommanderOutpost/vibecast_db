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
                "title": video["title"],
                "publishTime": video["publish_time"],
                "viewCount": video["view_count"],
            }
            for video in videos
        ]
    )
    return [str(video_id) for video_id in result.inserted_ids]


async def get_videos_by_channel_id(channel_id: str):
    cursor = db.videos.find({"channel_id": ObjectId(channel_id)})
    return [video async for video in cursor]
