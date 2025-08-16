# mcp_params.py
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# -------------------------
# API keys
# -------------------------
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
brave_api_key = os.getenv("BRAVE_API_KEY")
# Check what APIs are available
has_reddit = bool(reddit_client_id and reddit_client_secret)
has_twitter = bool(twitter_bearer_token)
has_youtube = bool(youtube_api_key)
has_brave = bool(brave_api_key)
# -------------------------
# Build env dicts (only include present values)
# -------------------------
def _make_env(d: dict):
    return {k: v for k, v in d.items() if v is not None and v != ""}

brave_env = _make_env({"BRAVE_API_KEY": brave_api_key})
reddit_env = _make_env({
    "REDDIT_CLIENT_ID": reddit_client_id,
    "REDDIT_CLIENT_SECRET": reddit_client_secret
})
twitter_env = _make_env({"TWITTER_BEARER_TOKEN": twitter_bearer_token})
youtube_env = _make_env({"YOUTUBE_API_KEY": youtube_api_key})

# Merge envs for trends server (only non-empty keys)
trends_env = {}
for e in (reddit_env, twitter_env, youtube_env, brave_env):
    trends_env.update(e)

# -------------------------
# MCP server commands
# -------------------------

content_accounts_mcp = {"command": "python", "args": ["profiles_server.py"], "env": {}}  
trends_mcp = {"command": "python", "args": ["trends_server.py"], "env": trends_env}
content_publishing_mcp = {"command": "python", "args": ["content_server.py"], "env": _make_env({
    "TWITTER_BEARER_TOKEN": twitter_bearer_token,
    "YOUTUBE_API_KEY": youtube_api_key
})}
resend_mcp = {"command": "python", "args": ["resend_server.py"], "env": {}}

curator_mcp_server_params = [
    content_accounts_mcp,
    resend_mcp,
    trends_mcp,
    content_publishing_mcp
]

# -------------------------
# Researcher MCP servers (for a researcher agent)
# -------------------------
def researcher_mcp_server_params(name: str):
    """Parameters to start supporting only the Brave Search MCP server."""
    params = [{
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": brave_env,
    }]

    return params

# -------------------------
# Content & platform config (unchanged semantics)
# -------------------------
CONTENT_CREATION_MODES = {
    "research_only": {
        "create_content": False,
        "research_depth": "deep",
        "platforms": []
    },
    "blog_focused": {
        "create_content": True,
        "research_depth": "medium",
        "platforms": ["blog"],
        "content_types": ["article", "analysis", "tutorial"]
    },
    "social_media_focused": {
        "create_content": True,
        "research_depth": "light",
        "platforms": ["twitter", "linkedin"],
        "content_types": ["post", "thread", "quick_take"]
    },
    "full_spectrum": {
        "create_content": True,
        "research_depth": "medium",
        "platforms": ["blog", "twitter", "linkedin", "newsletter"],
        "content_types": ["article", "post", "thread", "summary", "analysis"]
    }
}

PLATFORM_CONFIGS = {
    "blog": {"max_content_length": 5000, "optimal_length": 2000, "posting_frequency": "daily"},
    "twitter": {"max_content_length": 280, "optimal_length": 200, "posting_frequency": "multiple_daily"},
    "linkedin": {"max_content_length": 3000, "optimal_length": 1000, "posting_frequency": "daily"},
    "newsletter": {"max_content_length": 10000, "optimal_length": 3000, "posting_frequency": "weekly"}
}

TREND_THRESHOLDS = {"must_create": 80, "should_create": 60, "consider_create": 40, "skip_threshold": 25}

QUALITY_METRICS = {
    "trend_alignment": 0.3,
    "strategy_fit": 0.25,
    "engagement_potential": 0.2,
    "uniqueness": 0.15,
    "timeliness": 0.1
}

DEFAULT_CURATOR_SETTINGS = {
    "mode": "full_spectrum",
    "research_frequency": "hourly",
    "content_creation_frequency": "every_4_hours",
    "strategy_review_frequency": "daily",
    "trend_threshold": TREND_THRESHOLDS["consider_create"],
    "platforms": ["blog", "twitter", "linkedin"],
    "max_daily_content": 5,
    "enable_promotion": True,
    "enable_strategy_updates": True
}
