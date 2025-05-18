# libs/agents/extractors/headline.py
from libs.agents.prompts.headline_prompt import HEADLINE_PROMPT
from libs.agents.extractors.utils import sanitize_json_output
from config.config import openai_client


async def extract_headline(text: str, sentiments: dict) -> str:
    """
    Generate one-line headline from sentiment triplet.
    """
    payload = f"Scores: {sentiments}\n\n{text}"
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": HEADLINE_PROMPT + "\n\n" + payload}],
    )
    return sanitize_json_output(resp.choices[0].message.content.strip())["headline"]
