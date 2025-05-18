# libs/agents/prompts/other_prompts.py
"""
Prompts for miscellaneous insights not covered by the main extractors.
"""

OTHER_INSIGHTS_PROMPT = """
List each “other insight” you can glean from the comments.
• One insight per line
• No bullets, no numbering
• Keep each line short and direct
Return ONLY those lines.
"""

VIDEO_REQUESTS_PROMPT = """
Pick out any explicit video requests the audience makes.
If there are none, just output: None
Otherwise, return each request on its own line, no bullets or numbering.
"""
