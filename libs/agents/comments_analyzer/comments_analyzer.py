# libs/agents/comments_analyzer/comments_analyzer.py
"""
Pull YouTube-comment text from Mongo, enrich it with video + channel
metadata, run our extractor agents, and upsert the resulting analytics
document.

The added “Channel name / Video title” pre-amble gives every extractor
more context so it can reference the creator or the video naturally.
"""

import asyncio
from typing import Optional, Dict

from config.config import openai_client  # still used by sibling extractors
from libs.database.youtube.comments import get_comments_by_video_id
from libs.database.youtube.videos import get_video_by_id
from libs.database.youtube.channels import get_channel_by_id
from libs.database.youtube.analysis import (
    create_analysis,
    get_analysis_by_comment_id,
    update_analysis,
)

# extractor helpers ----------------------------------------------------------
from libs.agents.extractors.sentiment import extract_sentiments
from libs.agents.extractors.headline import extract_headline
from libs.agents.extractors.discussions import extract_discussions
from libs.agents.extractors.people import extract_people
from libs.agents.extractors.other import extract_other_insights, extract_video_requests


async def _meta_block(video_id: str) -> Optional[str]:
    """
    Build a context header such as:

        Channel name : Ludwig
        Video title  : I Tried Chessboxing
        Published    : 2023-01-02T18:00:05Z
        Views        : 1_234_567
        Likes        : 98_765
        Duration     : PT8M11S
        Description  : (first 300 chars…)

    Returns the block or None if lookup fails.
    """
    v = await get_video_by_id(video_id)
    if not v:
        return None

    c = await get_channel_by_id(v["channel_id"])
    if not c:
        return None

    desc = (v.get("description") or "").strip().replace("\n", " ")[:300]
    if len(desc) == 300:
        desc += "…"

    return (
        f"Channel name : {c['name']}\n"
        f"Video title  : {v['name']}\n"
        f"Published    : {v['publish_time']}\n"
        f"Views        : {v['view_count']}\n"
        f"Likes        : {v.get('like_count','NA')}\n"
        f"Duration     : {v.get('duration','NA')}\n"
        f"Description  : {desc}\n\n"
    )


async def analyze_and_store_comments(video_id: str) -> str:
    """
    Full pipeline: comments → extractors → (upsert) analysis doc.
    """
    comments_doc = await get_comments_by_video_id(video_id)
    if not comments_doc:
        # Nothing to analyse
        return ""

    meta = await _meta_block(video_id) or ""
    comments_text = "\n".join(comments_doc["comments"])

    # -----------------------------------------------------------------------
    # 1) run the extractors
    # -----------------------------------------------------------------------
    blob = meta + comments_text

    sentiments = await extract_sentiments(blob)
    headline_task = extract_headline(blob, sentiments)
    discussions_task = extract_discussions(blob)
    people_task = extract_people(
        blob, comments_text
    )  # keep raw comments for de-hallucination
    other_task = extract_other_insights(blob)
    requests_task = extract_video_requests(blob)

    headline, discussions, people, other, requests = await asyncio.gather(
        headline_task, discussions_task, people_task, other_task, requests_task
    )

    # -----------------------------------------------------------------------
    # 2) upsert the analysis document
    # -----------------------------------------------------------------------
    prev = await get_analysis_by_comment_id(video_id)
    fields: Dict = dict(
        sentiments=sentiments,
        headline=headline,
        discussions=discussions,
        people=people,
        other_insights=other,
        video_requests=requests,
    )

    if not prev:
        return await create_analysis(comment_id=video_id, **fields)

    if any(prev["analysis"].get(k) != v for k, v in fields.items()):
        await update_analysis(comment_id=video_id, **fields)

    return str(prev["_id"])
