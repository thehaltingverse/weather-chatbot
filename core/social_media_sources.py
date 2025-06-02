from typing import List, Dict
import praw

# # Functions to obtain social media data
def fetch_reddit_weather_posts(
    reddit_client_id: str,
    reddit_client_secret: str,
    reddit_user_agent: str,
    location: str,
    max_posts: int = 20,
) -> List[Dict]:
    """
    Fetch recent weather-related Reddit posts from select subreddits and subreddits matching the location name.

    Args:
        reddit_client_id (str): Reddit API client ID.
        reddit_client_secret (str): Reddit API client secret.
        reddit_user_agent (str): User agent string.
        location (str): City or city+state string, e.g. "Seattle WA"
        max_posts (int): Maximum number of posts to return.

    Returns:
        List[Dict]: List of posts dicts with keys: title, subreddit, created_utc, url, selftext
    """

    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent,
    )

    weather_subreddits = ["weather", "climate", "StormComing"]

    location_parts = location.lower().replace(",", "").split()
    location_subreddits = []

    for part in location_parts:
        # Search subreddits with location part in the name, limit 5 per part
        for sub in reddit.subreddits.search_by_name(part, exact=False)[:5]:
            sub_name = sub.display_name.lower()
            if any(loc_part in sub_name for loc_part in location_parts):
                location_subreddits.append(sub.display_name)

    # Unique combined list
    all_subreddits = list(set(weather_subreddits + location_subreddits))

    weather_keywords = [
        "weather", "storm", "flood", "rain", "snow", "heatwave",
        "tornado", "hurricane", "drought", "lightning", "climate",
        "hail", "wind"
    ]

    posts = []

    for subreddit_name in all_subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        query = " OR ".join(weather_keywords)
        # Search top posts in past week, sorted by relevance
        for submission in subreddit.search(query, time_filter="week", sort="relevance", limit=max_posts):
            posts.append({
                "title": submission.title,
                "subreddit": subreddit_name,
                "created_utc": submission.created_utc,
                "url": submission.url,
                "selftext": submission.selftext,
            })
            if len(posts) >= max_posts:
                break
        if len(posts) >= max_posts:
            break

    return posts
