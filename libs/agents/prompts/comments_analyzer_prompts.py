RULES = """
You are to provide an analysis of all the comments based on the following questions:
1.  Sentiment Analysis (Everything should be rated out of 100, Example: 50/100)
    i. What is the overall sentiment of the comments about the video?
    ii. What is the overall sentiment of the comments about the topic spoken about in the video?
    iii. What is the overall sentiment of the comments about the creator?
    
2. Major Discussions
    i. What are the major discussions in the comments?
    ii. What are the major discussions about the topic spoken about in the video?
    iii. What are the major discussions about the creator?
    
3. Other Insights
    i. What are the other insights you can provide about the comments?
    ii. What are the other insights you can provide about the topic spoken about in the video?
    iii. What are the other insights you can provide about the creator?
    iv. Are there any video requests in the comments?
    v. etc; think about more be creative and provide more insights.
    vi. What are the most common words used in the comments...ignore if generic.
"""


def generate_prompt(comments, analytics=None):
    """
    Generate a prompt for the comments analyzer agent.
    """
    prompt = f"""
    You are a comments analyzer agent. Your task is to analyze the comments and provide insights based on the rules provided.
    You will be provided with the rules, comments, and analytics. Your task is to provide an analysis based on the rules.
    If analytics are provided, your job is to analyze the comments and see if there are any changes from the previous analytics.
    If analytics are provided, and there are not much changes, just output The exact same analytics as provided.
    If there are no analytics provided, your job is to analyze the comments and provide insights based on the rules.

    Rules:
    {RULES}

    Comments:
    {comments}

    Analytics:
    {analytics}

    Please provide your analysis.
    """
    return prompt
