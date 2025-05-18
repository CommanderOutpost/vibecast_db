# libs/agents/extractors/people.py
import json, re
from libs.agents.prompts.people_prompt import PEOPLE_PROMPT
from config.config import openai_client
from libs.agents.extractors.utils import sanitize_json_output


def _name_in_comments(name: str, comments: str) -> bool:
    pattern = r"\b" + re.escape(name) + r"\b"
    return re.search(pattern, comments, re.IGNORECASE) is not None


async def extract_people(text: str, comments_blob: str) -> list:
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PEOPLE_PROMPT + "\n\n" + text}],
    )
    arr = sanitize_json_output(
        resp.choices[0].message.content.strip()
    )
    # drop hallucinations
    return [p for p in arr if _name_in_comments(p["name"], comments_blob)]
