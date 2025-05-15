from fastapi import HTTPException, status
from googleapiclient.discovery import build
from typing import List
from libs.database.youtube.comments import create_comments, get_comments_by_video_id
from libs.database.youtube.videos import get_video_by_id


async def get_youtube_comments(
    api_key: str, video_id: str, max_comments: int = 100
) -> List[str]:
    """
    Fetches top-level comments from a YouTube video.

    Args:
        api_key (str): Your YouTube Data API v3 key.
        video_id (str): The YouTube video ID to fetch comments from.
        max_comments (int): Maximum number of comments to fetch (default is 100).

    Returns:
        List[str]: A list of comment strings.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video document {video_id!r} not found",
        )

    youtube_video_id = video["youtube_video_id"]
    print("YouTube video ID:", youtube_video_id)
    print("Video ID:", video_id)

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=youtube_video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText",
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            if len(comments) >= max_comments:
                break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    await create_comments(video_id, comments)
    
    await get_comments_by_video_id("6824900b1b7239ca46abfe69")
    

    return comments
