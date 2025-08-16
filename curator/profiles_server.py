#!/usr/bin/env python3
"""MCP Server for Profile Management"""

from mcp.server.fastmcp import FastMCP
from profiles import ContentAccount
import json
from trends import get_top_trending_topics

# Create the MCP server
mcp = FastMCP("Content Accounts Server")

@mcp.resource("content-account://{name}")
async def read_content_account(name: str) -> str:
    """Read content account data"""
    account = ContentAccount.get(name)
    return account.report()

@mcp.resource("content-strategy://{name}")  
async def read_content_strategy(name: str) -> str:
    """Read content strategy for an account"""
    account = ContentAccount.get(name)
    return account.get_strategy()

@mcp.tool()
async def create_content(name: str, topic: str, platform: str, content_type: str, rationale: str) -> str:
    """Create content for a topic on a platform"""
    account = ContentAccount.get(name)
    return account.create_content(topic, platform, content_type, rationale)

@mcp.tool()
async def skip_content(name: str, topic: str, rationale: str) -> str:
    """Skip creating content for a topic"""
    account = ContentAccount.get(name)
    return account.skip_content(topic, rationale)

@mcp.tool()
async def promote_content(name: str, topic: str, platform: str, rationale: str) -> str:
    """Promote existing content to a new platform"""
    account = ContentAccount.get(name)
    return account.promote_existing_content(topic, platform, rationale)

@mcp.tool()
async def get_content_account_report(name: str) -> str:
    """Get detailed content account report"""
    account = ContentAccount.get(name)
    return account.report()

@mcp.tool()
async def get_content_performance_analysis(name: str) -> str:
    """Get content performance analysis and insights"""
    account = ContentAccount.get(name)
    analysis = account.analyze_performance()
    return json.dumps(analysis)

@mcp.tool()
async def get_recent_content(name: str, days: int = 7) -> str:
    """Get recent content created in the last N days"""
    account = ContentAccount.get(name)
    recent = account.get_recent_content(days)
    return str([content.model_dump() for content in recent])

@mcp.tool()
async def add_content_credits(name: str, amount: float) -> str:
    """Add credits to content account"""
    account = ContentAccount.get(name)
    account.add_credits(amount)
    return f"Added {amount} credits to {name}"

@mcp.tool()
async def change_content_strategy(name: str, strategy: str) -> str:
    """Change the content strategy"""
    account = ContentAccount.get(name)
    return account.change_strategy(strategy)

@mcp.tool()
async def reset_content_account(name: str, strategy: str) -> str:
    """Reset content account with new strategy"""
    account = ContentAccount.get(name)
    account.reset(strategy)
    return f"Reset account {name} with new strategy"

@mcp.tool()
async def get_top_performing_topics(name: str, limit: int = 5) -> str:
    """Get top performing topics by content count"""
    account = ContentAccount.get(name)
    top_topics = account.get_top_topics(limit)
    return json.dumps(top_topics)

@mcp.tool()
async def get_platform_performance(name: str) -> str:
    """Get performance metrics by platform"""
    account = ContentAccount.get(name)
    performance = account.get_platform_performance()
    return json.dumps(performance)

@mcp.tool()
async def get_top_trends(limit: int = 5) -> str:
    """Get today's top AI trends"""
    trends = get_top_trending_topics(limit)
    return json.dumps([t.to_dict() for t in trends])

if __name__ == "__main__":
    mcp.run(transport='stdio')