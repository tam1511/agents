from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime, timedelta
import random
from database import write_trends, read_trends
from functools import lru_cache
import tweepy

load_dotenv(override=True)

# API Keys
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
hackernews_base_url = "https://hacker-news.firebaseio.com/v0"

# Trend scoring weights
REDDIT_WEIGHT = 0.3
TWITTER_WEIGHT = 0.25
HACKERNEWS_WEIGHT = 0.25
YOUTUBE_WEIGHT = 0.2

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "neural networks",
    "GPT", "Claude", "ChatGPT", "LLM", "large language model", "generative AI",
    "computer vision", "natural language processing", "NLP", "transformer",
    "OpenAI", "Anthropic", "Google AI", "Meta AI", "AI research", "AGI",
    "reinforcement learning", "diffusion models", "stable diffusion", "midjourney",
    "AI ethics", "AI safety", "AI regulation", "AI governance", "AI bias",
    "robotics", "autonomous", "AI startup", "AI funding", "AI breakthrough"
]


class TrendData:
    def __init__(self, topic: str, score: float, sources: dict, timestamp: str):
        self.topic = topic
        self.score = score
        self.sources = sources  # {platform: engagement_count}
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            "topic": self.topic,
            "score": self.score,
            "sources": self.sources,
            "timestamp": self.timestamp
        }


def get_reddit_ai_trends() -> dict[str, float]:
    """Get trending AI topics from Reddit"""
    try:
        if not reddit_client_id or not reddit_client_secret:
            return {}
        
        # Reddit API authentication
        auth = requests.auth.HTTPBasicAuth(reddit_client_id, reddit_client_secret)
        data = {'grant_type': 'client_credentials', 'username': 'ai-curator-bot', 'password': ''}
        headers = {'User-Agent': 'AI-Curator/0.1'}
        
        response = requests.post('https://www.reddit.com/api/v1/access_token',
                               auth=auth, data=data, headers=headers)
        token = response.json()['access_token']
        headers['Authorization'] = f'bearer {token}'
        
        # Get hot posts from AI-related subreddits
        subreddits = ['MachineLearning', 'artificial', 'OpenAI', 'singularity', 'technology']
        trends = {}
        
        for subreddit in subreddits:
            url = f'https://oauth.reddit.com/r/{subreddit}/hot'
            response = requests.get(url, headers=headers, params={'limit': 25})
            
            if response.status_code == 200:
                posts = response.json()['data']['children']
                for post in posts:
                    title = post['data']['title'].lower()
                    score = post['data']['score']
                    
                    # Check if title contains AI keywords
                    for keyword in AI_KEYWORDS:
                        if keyword.lower() in title:
                            trends[keyword] = trends.get(keyword, 0) + score
        
        return trends
    except Exception as e:
        print(f"Error fetching Reddit trends: {e}")
        return {}


def get_hackernews_ai_trends() -> dict[str, float]:
    """Get trending AI topics from Hacker News"""
    try:
        # Get top stories
        response = requests.get(f"{hackernews_base_url}/topstories.json")
        story_ids = response.json()[:50]  # Top 50 stories
        
        trends = {}
        
        for story_id in story_ids:
            story_response = requests.get(f"{hackernews_base_url}/item/{story_id}.json")
            story = story_response.json()
            
            if story and 'title' in story:
                title = story['title'].lower()
                score = story.get('score', 0)
                
                # Check if title contains AI keywords
                for keyword in AI_KEYWORDS:
                    if keyword.lower() in title:
                        trends[keyword] = trends.get(keyword, 0) + score
        
        return trends
    except Exception as e:
        print(f"Error fetching HackerNews trends: {e}")
        return {}


def get_youtube_ai_trends() -> dict[str, float]:
    """Get trending AI topics from YouTube"""
    try:
        if not youtube_api_key:
            return {}
            
        trends = {}
        
        for keyword in AI_KEYWORDS[:10]:  # Limit API calls
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': keyword,
                'type': 'video',
                'order': 'relevance',
                'publishedAfter': (datetime.now() - timedelta(days=7)).isoformat() + 'Z',
                'maxResults': 10,
                'key': youtube_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                videos = response.json().get('items', [])
                total_engagement = sum(1 for video in videos)  # Simplified engagement
                trends[keyword] = trends.get(keyword, 0) + total_engagement * 100
        
        return trends
    except Exception as e:
        print(f"Error fetching YouTube trends: {e}")
        return {}


def get_twitter_ai_trends() -> dict[str, float]:
    """Get trending AI topics from Twitter (X)"""
    try:
        if not twitter_bearer_token:
            return {}
            
        # Using tweepy for Twitter API v2
        client = tweepy.Client(bearer_token=twitter_bearer_token)
        trends = {}
        
        for keyword in AI_KEYWORDS[:10]:  # Limit API calls
            tweets = client.search_recent_tweets(
                query=f'"{keyword}" -is:retweet',
                max_results=10,
                tweet_fields=['public_metrics']
            )
            
            if tweets.data:
                total_engagement = sum(
                    tweet.public_metrics['like_count'] + 
                    tweet.public_metrics['retweet_count']
                    for tweet in tweets.data
                )
                trends[keyword] = trends.get(keyword, 0) + total_engagement
        
        return trends
    except Exception as e:
        print(f"Error fetching Twitter trends: {e}")
        return {}


def calculate_trend_score(topic: str, source_data: dict) -> float:
    """Calculate weighted trend score from multiple sources"""
    reddit_score = source_data.get('reddit', 0) * REDDIT_WEIGHT
    twitter_score = source_data.get('twitter', 0) * TWITTER_WEIGHT
    hackernews_score = source_data.get('hackernews', 0) * HACKERNEWS_WEIGHT
    youtube_score = source_data.get('youtube', 0) * YOUTUBE_WEIGHT
    
    total_score = reddit_score + twitter_score + hackernews_score + youtube_score
    
    # Normalize to 0-100 scale
    return min(100, max(0, total_score / 100))


@lru_cache(maxsize=2)
def get_trends_for_date(today):
    """Get cached trends for a specific date"""
    trends_data = read_trends(today)
    if not trends_data:
        trends_data = fetch_all_ai_trends()
        write_trends(today, trends_data)
    return trends_data


def fetch_all_ai_trends() -> dict[str, TrendData]:
    """Fetch trends from all sources and combine them"""
    reddit_trends = get_reddit_ai_trends()
    hackernews_trends = get_hackernews_ai_trends()
    youtube_trends = get_youtube_ai_trends()
    twitter_trends = get_twitter_ai_trends()
    
    # Combine all trends
    all_topics = set(reddit_trends.keys()) | set(hackernews_trends.keys()) | \
                set(youtube_trends.keys()) | set(twitter_trends.keys())
    
    trend_objects = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for topic in all_topics:
        source_data = {
            'reddit': reddit_trends.get(topic, 0),
            'hackernews': hackernews_trends.get(topic, 0),
            'youtube': youtube_trends.get(topic, 0),
            'twitter': twitter_trends.get(topic, 0)
        }
        
        score = calculate_trend_score(topic, source_data)
        trend_objects[topic] = TrendData(topic, score, source_data, timestamp)
    
    return trend_objects


def get_trend_score(topic: str) -> float:
    """Get trend score for a specific topic"""
    today = datetime.now().date().strftime("%Y-%m-%d")
    trends_data = get_trends_for_date(today)
    
    if topic in trends_data:
        return trends_data[topic].score
    
    # Fallback: check if topic contains any AI keywords
    for keyword in AI_KEYWORDS:
        if keyword.lower() in topic.lower() and keyword in trends_data:
            return trends_data[keyword].score * 0.7  # Reduced score for partial match
    
    return 0.0


def get_top_trending_topics(limit: int = 10) -> list[TrendData]:
    """Get top trending AI topics"""
    today = datetime.now().date().strftime("%Y-%m-%d")
    trends_data = get_trends_for_date(today)
    
    # Sort by score and return top N
    sorted_trends = sorted(trends_data.values(), key=lambda x: x.score, reverse=True)
    return sorted_trends[:limit]


def get_mock_trend_score(topic: str) -> float:
    """Mock trend score for testing when APIs are not available"""
    # Simple hash-based mock scoring for consistency
    score = hash(topic + datetime.now().date().strftime("%Y-%m-%d")) % 100
    return float(score)


# Main function to get trend score (with fallback)
def get_trend_score_with_fallback(topic: str) -> float:
    """Get trend score with fallback to mock data if APIs fail"""
    try:
        return get_trend_score(topic)
    except Exception as e:
        print(f"Error getting trend score for {topic}: {e}, using mock data")
        return get_mock_trend_score(topic)


if __name__ == "__main__":
    # Test the trend scoring system
    trends = get_top_trending_topics(5)
    for trend in trends:
        print(f"{trend.topic}: {trend.score:.2f}")
        print(f"  Sources: {trend.sources}")
        print()