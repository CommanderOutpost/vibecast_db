import json
from config.config import openai_client
from libs.database.youtube.comments import (
    get_comments_by_video_id,
)
from libs.agents.prompts.comments_analyzer_prompts import generate_prompt
from libs.database.youtube.analysis import (
    create_analysis,
    get_analysis_by_comment_id,
    update_analysis,
)
from libs.agents.analytics_extractor.analytics_extractor import (
    extract_sentiment_ratings,
    extract_major_discussions,
    extract_other_insights,
    extract_video_requests,
)


async def analyze_comments(
    video_id: str, analytics: str = None, model: str = "gpt-4o-mini"
) -> str:
    """
    Analyze the comments (or previous analytics) for a given video ID.
    If `analytics` is provided, the AI will only update sections with major changes.
    """
    comments_doc = await get_comments_by_video_id(video_id)
    if not comments_doc:
        return ""

    prompt = generate_prompt(comments_doc["comments"], analytics)
    response = openai_client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def analyze_and_store_comments(video_id: str) -> str:
    """
    Full pipeline: load prior analysis, run AI, extract fields, normalize defaults,
    then create or update the DB record.
    """
    prev = await get_analysis_by_comment_id(video_id)
    analytics_json = (
        json.dumps(prev["analysis"]) if prev and prev.get("analysis") else None
    )

    analysis_text = await analyze_comments(video_id, analytics_json)
    if not analysis_text:
        return ""

    # Extract and normalize
    sent = extract_sentiment_ratings(analysis_text) or {
        k: None for k in ("video_sentiment", "topic_sentiment", "creator_sentiment")
    }

    def safe_extract(func, default):
        try:
            result = func(analysis_text)
            return result or default
        except Exception:
            return default

    major = safe_extract(
        extract_major_discussions, {"video": [], "topic": [], "creator": []}
    )
    for key in ("video", "topic", "creator"):
        major.setdefault(key, [])

    insights = safe_extract(extract_other_insights, [])
    requests = safe_extract(extract_video_requests, [])

    # Determine update vs create
    if not prev:
        return await create_analysis(
            comment_id=video_id,
            sentiments=sent,
            major_discussions=major,
            other_insights=insights,
            video_requests=requests,
        )

    # Build diffed fields
    fields = {}
    if sent != prev["analysis"]["sentiments"]:
        fields["sentiments"] = sent
    if major != prev["analysis"]["major_discussions"]:
        fields["major_discussions"] = major
    if insights != prev["analysis"]["other_insights"]:
        fields["other_insights"] = insights
    if requests != prev["analysis"].get("video_requests", []):
        fields["video_requests"] = requests

    if fields:
        await update_analysis(comment_id=video_id, **fields)
    return str(prev["_id"])
