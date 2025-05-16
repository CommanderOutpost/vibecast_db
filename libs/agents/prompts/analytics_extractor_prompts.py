SENTIMENT_EXTRACTION_RULES = """
You are to extract the sentiment ratings given in a specific text.
The ratings are given in the format of "X/100" where X is a number between 0 and 100.
The ratings are given for the following categories:
1. Overall sentiment of the comments about the video
2. Overall sentiment of the comments about the topic spoken about in the video
3. Overall sentiment of the comments about the creator

Please extract the ratings for each category and provide them in the following format:
video_sentiment, topic_sentiment, creator_sentiment
For example: 
    Input text: "The overall sentiment of the comments about the video is 80/100, the overall sentiment of the comments about the topic spoken about in the video is 70/100, and the overall sentiment of the comments about the creator is 90/100."
    Output: 80, 70, 90
If the ratings are not present in the text, please return None for that category.
For example:
80, 70, None
"""

MAJOR_DISCUSSIONS_RULES = """
You must extract the major discussion topics and output exactly one JSON object—nothing else. 
That JSON must have exactly three keys: "video", "topic", and "creator", each mapping to an array of concise strings.
Do not include any prose, bullets, or extra fields—only the JSON object itself.
For example:
{
  "video": ["discussion A", "discussion B"],
  "topic": ["discussion about X"],
  "creator": ["discussion about Y"]
}
If there are no discussion for a category, return an empty array for that category.
For example:
{
  "video": [],
  "topic": ["discussion about X"],
  "creator": []
}
"""

OTHER_INSIGHTS_RULES = """
You are to extract “other insights” from the text.
List each insight as one line (if too long, summarize into one line), phrasing it clearly and briefly.
No numbering or bullets, or anything like that just the insights, one per line.
"""

VIDEO_REQUESTS_RULES = """
You are to extract any video requests from the provided comments text.
List each request as a single concise line. If there are no requests, just output "None".
"""
