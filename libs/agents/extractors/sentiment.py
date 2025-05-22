# libs/agents/extractors/sentiment.py
import json
from libs.agents.prompts.sentiment_prompt import SENTIMENT_PROMPT
from libs.agents.extractors.utils import sanitize_json_output
from config.config import openai_client


async def extract_sentiments(text: str) -> dict:
    """
    Returns e.g.
    {
      "video":   {"positive": 60, "neutral": 30, "negative": 10},
      "creator": {"positive": 55, "neutral": 35, "negative": 10},
      "topic":   {"positive": 40, "neutral": 45, "negative": 15}
    }
    """
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": SENTIMENT_PROMPT + "\n\n" + text}],
    )
    return sanitize_json_output(resp.choices[0].message.content.strip())
