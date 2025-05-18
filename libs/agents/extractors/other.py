# libs/agents/extractors/other.py
"""
Extractors for:
1. miscellaneous “other insights”
2. audience video requests

Both return plain Python lists.  They never raise on bad JSON;
instead they fall back to an empty list so the calling pipeline
can continue gracefully.
"""

import json
from typing import List

from config.config import openai_client
from libs.agents.extractors.utils import sanitize_json_output
from libs.agents.prompts.other_prompts import (
    OTHER_INSIGHTS_PROMPT,
    VIDEO_REQUESTS_PROMPT,
)


async def _chat(prompt: str) -> str:
    """Internal helper — one-shot chat call with the mini model."""
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


async def extract_other_insights(text: str) -> List[str]:
    """
    Return a list of terse insight lines, or [] if none found.
    """
    raw = await _chat(OTHER_INSIGHTS_PROMPT + "\n\n" + text)

    # Try JSON first in case the model wrapped an array.
    try:
        maybe_json = sanitize_json_output(raw)
        if isinstance(maybe_json, list):
            return [s.strip() for s in maybe_json if s.strip()]
    except ValueError:
        pass

    # Fallback: treat each non-empty newline as one insight.
    return [
        line.strip()
        for line in raw.splitlines()
        if line.strip() and line.lower() != "none"
    ]


async def extract_video_requests(text: str) -> List[str]:
    """
    Return list of requested video ideas.  Empty list if none (or if model writes 'None').
    """
    raw = await _chat(VIDEO_REQUESTS_PROMPT + "\n\n" + text)

    # Accept JSON array or newline list.
    try:
        arr = sanitize_json_output(raw)
        if isinstance(arr, list):
            return [r.strip() for r in arr if r.strip()]
    except ValueError:
        pass

    if raw.lower() == "none":
        return []

    return [line.strip() for line in raw.splitlines() if line.strip()]
