DISCUSSIONS_PROMPT = """
For each category—video, creator, and topic—identify up to five discussion themes.  
For every theme, count how many times it was mentioned in the comments, and compute a sentiment breakdown (positive/neutral/negative percentages that sum to 100).  
Return exactly one JSON object, with keys "video", "creator", and "topic", each mapping to an array of objects with this shape:

{
  "name": "<the theme phrase>",
  "mentions": <integer count>,
  "sentiment": {
    "positive": <int 0-100>,
    "neutral":  <int 0-100>,
    "negative": <int 0-100>
  }
}

Example:
{
  "video": [
    {
      "name": "editing transitions",
      "mentions": 342,
      "sentiment": { "positive": 85, "neutral": 10, "negative": 5 }
    },
    …
  ],
  "creator": [ … ],
  "topic":   [ … ]
}

No prose, no extra fields, valid JSON only.
"""
