# libs/youtube/get_all_videos_from_channel.py
from fastapi import HTTPException, status
from googleapiclient.discovery import build
from typing import List, Dict
from libs.database.youtube.channels import get_channel_by_id
from libs.database.youtube.videos import create_videos
import logging

logger = logging.getLogger(__name__)


async def get_all_videos_from_channel(api_key: str, channel_id: str) -> List[Dict]:
    """
    Crawl every video in the channel’s “uploads” playlist, pull rich metadata,
    stash to Mongo, and return the list we saved.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    # 1) look up our Channel doc
    ch_doc = await get_channel_by_id(channel_id)
    if not ch_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel document {channel_id!r} not found",
        )

    uploads_pid = (
        youtube.channels()
        .list(part="contentDetails", id=ch_doc["youtube_channel_id"])
        .execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    )

    videos: List[Dict] = []
    next_page = None

    while True:
        playlist_resp = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=uploads_pid,
                maxResults=50,
                pageToken=next_page,
            )
            .execute()
        )

        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in playlist_resp.get("items", [])
        ]
        if not video_ids:
            break

        details_resp = (
            youtube.videos()
            .list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids),
                maxResults=50,
            )
            .execute()
        )

        for item in details_resp.get("items", []):
            snip = item["snippet"]
            stats = item["statistics"]
            cdet = item["contentDetails"]

            videos.append(
                {
                    "name": snip["title"],
                    "description": snip.get("description"),
                    "youtube_video_id": item["id"],
                    "publish_time": snip["publishedAt"],
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": (
                        int(stats.get("likeCount", 0)) if "likeCount" in stats else None
                    ),
                    "comment_count": (
                        int(stats.get("commentCount", 0))
                        if "commentCount" in stats
                        else None
                    ),
                    "duration": cdet.get("duration"),  # ISO 8601
                    "channel_id": channel_id,
                }
            )

        next_page = playlist_resp.get("nextPageToken")
        if not next_page:
            break

    if videos:
        await create_videos(videos)

    return videos
