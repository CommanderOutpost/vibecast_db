from googleapiclient.discovery import build
from typing import Dict, Optional
import os


def get_channel_info_by_handle(handle: str, api_key: Optional[str] = None) -> Dict:
    """
    Given a YouTube channel handle (legacy username or @handle), return the
    channel's metadata and statistics.

    Steps:
      1) Try to look up via forUsername (works for legacy usernames).
      2) If no results, perform a search for "@handle" and grab the first channelId.
      3) Use channels.list with part=snippet,statistics,contentDetails to fetch full info.

    Raises:
      ValueError if no channel is found.
    """
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise ValueError("An API key must be provided or set in YOUTUBE_API_KEY")

    youtube = build("youtube", "v3", developerKey=key)

    # 1) Attempt legacy-username lookup
    resp = (
        youtube.channels()
        .list(part="snippet,statistics,contentDetails", forUsername=handle)
        .execute()
    )

    items = resp.get("items", [])
    channel_id = None

    if items:
        # Found via legacy username
        channel_id = items[0]["id"]
    else:
        # 2) Fallback: search by @handle
        query = handle if handle.startswith("@") else f"@{handle}"
        search_resp = (
            youtube.search()
            .list(part="snippet", q=query, type="channel", maxResults=1)
            .execute()
        )
        search_items = search_resp.get("items", [])
        if not search_items:
            raise ValueError(f"No channel found matching handle {handle!r}")
        channel_id = search_items[0]["snippet"]["channelId"]

    # 3) Fetch full channel info
    final = (
        youtube.channels()
        .list(part="snippet,statistics,contentDetails", id=channel_id)
        .execute()
    )

    channels = final.get("items", [])
    if not channels:
        raise ValueError(f"Channel ID {channel_id!r} returned no data")

    # Return the first channel’s dict
    return channels[0]


# Example usage:
if __name__ == "__main__":
    info = get_channel_info_by_handle("@ludwig")
    print("Title:", info["snippet"]["title"])
    print("Subscribers:", info["statistics"]["subscriberCount"])
    print("Uploads playlist:", info["contentDetails"]["relatedPlaylists"]["uploads"])
    print(info)