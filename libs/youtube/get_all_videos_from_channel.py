from googleapiclient.discovery import build
from typing import List, Dict


def get_all_videos_from_channel(api_key: str, channel_id: str) -> List[Dict]:
    """
    Fetches all videos from a YouTube channel using its uploads playlist.

    Args:
        api_key (str): YouTube Data API key.
        channel_id (str): The channel's unique ID (e.g. 'UC_x5XG1OV2P6uZZ5FSM9Ttw').

    Returns:
        List[Dict]: List of dicts with 'videoId', 'title', 'viewCount', and 'publishTime'.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    # Step 1: Get the Uploads playlist ID
    channel_response = (
        youtube.channels().list(part="contentDetails", id=channel_id).execute()
    )

    uploads_playlist_id = channel_response["items"][0]["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]

    # Step 2: Get all videos from the uploads playlist
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

        video_ids = []
        for item in playlist_response["items"]:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])

        # Step 3: Fetch video details
        video_details_response = (
            youtube.videos()
            .list(part="statistics,snippet", id=",".join(video_ids))
            .execute()
        )

        for item in video_details_response["items"]:
            video_id = item["id"]
            title = item["snippet"]["title"]
            publish_time = item["snippet"]["publishedAt"]
            view_count = item["statistics"].get("viewCount", "0")
            videos.append(
                {
                    "videoId": video_id,
                    "title": title,
                    "publishTime": publish_time,
                    "viewCount": view_count,
                }
            )

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    return videos
