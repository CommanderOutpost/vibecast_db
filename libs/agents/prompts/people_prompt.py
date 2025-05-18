PEOPLE_PROMPT = """
Identify up to six named people (or entities) repeatedly mentioned in the comments.
For each, estimate sentiment split and supply up to three concise remarks.
Return JSON array only; e.g.

[
  {
    "name": "Joe",
    "sentiment": {"positive": 68, "neutral": 22, "negative": 10},
    "remarks": ["Joe's editing skills praised", "Viewers want more tutorials"]
  }
]
"""
