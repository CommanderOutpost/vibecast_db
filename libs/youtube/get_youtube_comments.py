from fastapi import HTTPException, status
from googleapiclient.discovery import build
from typing import List, Dict, Any
from libs.database.youtube.comments import create_comments
from libs.database.youtube.videos import get_video_by_id


async def get_youtube_comments(
    api_key: str, video_id: str, max_comments: int = 100
) -> List[Dict[str, Any]]:
    """
    Fetches up to `max_comments` most relevant top-level comments plus their
    embedded replies (YouTube returns up to two per thread).

    Returns a list of dicts, each with:
      - 'text': the comment text
      - 'replies': list of the embedded reply texts
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video document {video_id!r} not found",
        )
    yt_id = video["youtube_video_id"]

    comments: List[Dict[str, Any]] = []
    page_token = None

    while len(comments) < max_comments:
        resp = (
            youtube.commentThreads()
            .list(
                part="snippet,replies",
                videoId=yt_id,
                maxResults=max_comments,
                pageToken=page_token,
                order="relevance",
                textFormat="plainText",
            )
            .execute()
        )

        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]
            sn = top["snippet"]

            entry = {"text": sn["textDisplay"], "replies": []}

            # <-- correct path here
            for r in item.get("replies", {}).get("comments", []):
                entry["replies"].append(r["snippet"]["textDisplay"])

            comments.append(entry)
            if len(comments) >= max_comments:
                break

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    # persist only the top-level comment texts
    await create_comments(video_id, comments)

    return comments
