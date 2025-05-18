SENTIMENT_PROMPT = """
Return **only** this JSON:

{
  "video": <0-100 integer>,
  "creator": <0-100 integer>,
  "topic": <0-100 integer>
}

where:
- "video" = overall sentiment towards the video itself,
- "creator" = sentiment towards the person who made it,
- "topic" = sentiment towards the subject matter discussed.

Do not write anything outside the braces.
"""
