from fastapi import HTTPException, status
from googleapiclient.discovery import build
from typing import List, Dict
from libs.database.youtube.channels import get_channel_by_id
from libs.database.youtube.videos import create_videos
import logging

logger = logging.getLogger(__name__)


async def get_all_videos_from_channel(api_key: str, channel_id: str) -> List[Dict]:
    """
    Fetches all videos from a YouTube channel using its uploads playlist.
    If the channel doesn't exist or is inaccessible, returns [].
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    # 1) look up our Channel doc
    ch_doc = await get_channel_by_id(channel_id)
    if not ch_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel document {channel_id!r} not found",
        )
        
    print(f"Channel doc: {ch_doc}")

    # 2) ask YouTube for that channel’s uploads playlist
    channel_response = (
        youtube.channels()
        .list(part="contentDetails", id=ch_doc["youtube_channel_id"])
        .execute()
    )

    items = channel_response.get("items")
    if not items:
        logger.warning(
            "No YouTube channel found or accessible with ID %s",
            ch_doc["youtube_channel_id"],
        )
        return []

    uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page_token = None

    while True:
        playlist_response = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            .execute()
        )

        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in playlist_response.get("items", [])
        ]

        if not video_ids:
            break

        video_details_response = (
            youtube.videos()
            .list(part="statistics,snippet", id=",".join(video_ids))
            .execute()
        )

        for item in video_details_response.get("items", []):
            videos.append(
                {
                    "name": item["snippet"]["title"],
                    "youtube_video_id": item["id"],
                    "publish_time": item["snippet"]["publishedAt"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "channel_id": channel_id,
                }
            )

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    if videos:
        await create_videos(videos)

    return videos
