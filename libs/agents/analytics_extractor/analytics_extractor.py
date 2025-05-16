import json, re
from typing import List
from config.config import openai_client
from libs.agents.prompts.analytics_extractor_prompts import (
    MAJOR_DISCUSSIONS_RULES,
    OTHER_INSIGHTS_RULES,
    SENTIMENT_EXTRACTION_RULES,
    VIDEO_REQUESTS_RULES,
)


def sanitize_json_output(raw: str) -> dict:
    """
    Pulls out the first `{…}` JSON blob from raw model output and parses it.
    Raises ValueError if no JSON found or if parsing fails.
    """
    # Grab the first brace-enclosed chunk
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    blob = match.group(1)
    try:
        return json.loads(blob)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def extract_sentiment_ratings(text: str) -> dict:
    """
    Extract sentiment ratings from the given text.
    """
    # Call the OpenAI API to extract the sentiment ratings
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": SENTIMENT_EXTRACTION_RULES + text}],
    )

    # Extract the sentiment ratings from the response
    sentiment_ratings = response.choices[0].message.content.strip()

    # Parse the sentiment ratings
    try:
        video_sentiment, topic_sentiment, creator_sentiment = map(
            int, sentiment_ratings.split(",")
        )
        return {
            "video_sentiment": video_sentiment,
            "topic_sentiment": topic_sentiment,
            "creator_sentiment": creator_sentiment,
        }
    except ValueError:
        return {}


def extract_major_discussions(text: str) -> list[str]:
    """
    Pull out the top recurring discussion topics,
    returning each as a one-line summary.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": MAJOR_DISCUSSIONS_RULES + "\n\n" + text}],
    )
    raw = response.choices[0].message.content.strip()
    return sanitize_json_output(raw)


def extract_other_insights(text: str) -> list[str]:
    """
    Pull out miscellaneous “other insights” from comments,
    returning each as a one-line summary.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": OTHER_INSIGHTS_RULES + "\n\n" + text}],
    )
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def extract_video_requests(text: str) -> List[str]:
    """
    Extract any video requests, return as plain list.
    """
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": VIDEO_REQUESTS_RULES + "\n\n" + text}],
    )
    raw = resp.choices[0].message.content.strip()
    # Expecting either JSON array or lines. Try JSON first:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback: one line per request
        return [line for line in raw.split("\n") if line.strip()]
