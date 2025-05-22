# libs/agents/extractors/discussions.py
from libs.agents.prompts.discussions_prompt import DISCUSSIONS_PROMPT
from libs.agents.extractors.utils import sanitize_json_output
from config.config import openai_client


async def extract_discussions(text: str) -> dict:
    """
    Returns:
      {
        "video":   [ {name, mentions, sentiment}, … ],
        "creator": [ … ],
        "topic":   [ … ]
      }
    """
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": DISCUSSIONS_PROMPT + "\n\n" + text}],
    )
    # sanitize_json_output will pull the exact JSON object out of the reply
    return sanitize_json_output(resp.choices[0].message.content.strip())
