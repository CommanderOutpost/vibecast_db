from googleapiclient.discovery import build
from typing import List


def get_youtube_comments(
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

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
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

    return comments
