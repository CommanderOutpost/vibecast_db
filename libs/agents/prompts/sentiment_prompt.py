SENTIMENT_PROMPT = """
Return **only** this JSON:

{
  "video":   {"positive": <int>, "neutral": <int>, "negative": <int>},
  "creator": {"positive": <int>, "neutral": <int>, "negative": <int>},
  "topic":   {"positive": <int>, "neutral": <int>, "negative": <int>}
}

Rules:
• Every number is 0-100   • Each object must sum to 100
• No prose, no extra keys
"""
