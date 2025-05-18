DISCUSSIONS_PROMPT = """
List the five most common discussion themes under each category.
Video: Discussions about the video content.
Creator: Discussions about the creator of the video.
Topic: Discussions about the topic of the video.
Do not include any other information.
Return exactly this JSON:

{
  "video": ["..."],
  "creator": ["..."],
  "topic": ["..."]
}

Use short phrases (max ~8 words) and never more than five per array.
"""
