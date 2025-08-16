#!/usr/bin/env python3
"""MCP Server for AI Trends Data"""

from mcp.server.fastmcp import FastMCP
from trends import (
    get_trend_score_with_fallback,
    get_top_trending_topics,
    fetch_all_ai_trends,
    AI_KEYWORDS
)
import json

# Create the MCP server
mcp = FastMCP("AI Trends Server")

@mcp.tool()
def get_trend_score(topic: str) -> str:
    """Get trend score for a specific AI topic"""
    score = get_trend_score_with_fallback(topic)
    return f"Trend score for '{topic}': {score:.2f}/100"

@mcp.tool()
def get_trending_ai_topics(limit: int = 10) -> str:
    """Get top trending AI topics with scores and sources"""
    try:
        trending = get_top_trending_topics(limit)
        results = [
            {
                "topic": trend.topic,
                "score": round(trend.score, 2),
                "sources": trend.sources,
                "timestamp": trend.timestamp
            }
            for trend in trending
        ]
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching trending topics: {e}"

@mcp.tool()
def get_ai_keywords() -> str:
    """Get the list of AI keywords being tracked"""
    return json.dumps({
        "keywords": AI_KEYWORDS,
        "total_count": len(AI_KEYWORDS),
        "description": "AI-related keywords and phrases being monitored for trends"
    }, indent=2)

@mcp.tool()
def search_trending_by_keyword(keyword: str, limit: int = 5) -> str:
    """Search for trending topics containing a specific keyword"""
    try:
        all_trends = get_top_trending_topics(50)  # fetch larger pool
        matching_trends = [
            {
                "topic": trend.topic,
                "score": round(trend.score, 2),
                "sources": trend.sources,
                "timestamp": trend.timestamp
            }
            for trend in all_trends if keyword.lower() in trend.topic.lower()
        ][:limit]
        return json.dumps({
            "keyword": keyword,
            "matching_trends": matching_trends,
            "count": len(matching_trends)
        }, indent=2)
    except Exception as e:
        return f"Error searching trends by keyword: {e}"

@mcp.tool()
def get_trend_sources_breakdown() -> str:
    """Get breakdown of trend data sources and their contributions"""
    try:
        trending = get_top_trending_topics(20)

        # Dynamically detect all sources
        all_sources = set()
        for trend in trending:
            all_sources.update(trend.sources.keys())

        source_stats = {src: {"total": 0, "count": 0} for src in all_sources}

        # Populate totals
        for trend in trending:
            for src, value in trend.sources.items():
                if value > 0:
                    source_stats[src]["total"] += value
                    source_stats[src]["count"] += 1

        # Calculate averages
        for src in source_stats:
            if source_stats[src]["count"] > 0:
                source_stats[src]["average"] = source_stats[src]["total"] / source_stats[src]["count"]
            else:
                source_stats[src]["average"] = 0

        return json.dumps({
            "source_breakdown": source_stats,
            "total_trending_topics": len(trending),
            "description": "Breakdown of trend data sources and their contributions"
        }, indent=2)
    except Exception as e:
        return f"Error getting source breakdown: {e}"

@mcp.tool()
def evaluate_content_opportunity(topic: str, platform: str) -> str:
    """Evaluate a content opportunity based on trend score and platform fit"""
    try:
        score = get_trend_score_with_fallback(topic)

        platform_multipliers = {
            "twitter": 1.2,
            "linkedin": 0.9,
            "blog": 1.1,
            "newsletter": 0.8
        }
        adjusted_score = score * platform_multipliers.get(platform.lower(), 1.0)

        if adjusted_score >= 70:
            recommendation = "STRONG CREATE - High trend score, excellent opportunity"
        elif adjusted_score >= 50:
            recommendation = "CREATE - Good trend score, solid opportunity"
        elif adjusted_score >= 30:
            recommendation = "CONSIDER - Moderate trend score, evaluate against strategy"
        else:
            recommendation = "SKIP - Low trend score, better opportunities available"

        trends_cache = fetch_all_ai_trends()
        timestamp = "unknown"
        if trends_cache:
            timestamp = next(iter(trends_cache.values())).timestamp

        return json.dumps({
            "topic": topic,
            "platform": platform,
            "raw_trend_score": round(score, 2),
            "platform_adjusted_score": round(adjusted_score, 2),
            "recommendation": recommendation,
            "evaluation_timestamp": timestamp
        }, indent=2)
    except Exception as e:
        return f"Error evaluating content opportunity: {e}"

@mcp.tool()
def get_content_timing_recommendation(topic: str) -> str:
    """Get timing recommendation for content creation based on trend analysis"""
    try:
        score = get_trend_score_with_fallback(topic)
        if score >= 80:
            timing = "URGENT - Create within 2-4 hours while trend is hot"
        elif score >= 60:
            timing = "SOON - Create within 24 hours to capitalize on trend"
        elif score >= 40:
            timing = "NORMAL - Create within 2-3 days, trend is stable"
        elif score >= 25:
            timing = "FLEXIBLE - No urgency, can schedule when convenient"
        else:
            timing = "LOW PRIORITY - Consider skipping or saving for later"

        urgency = "high" if score >= 70 else "medium" if score >= 40 else "low"

        return json.dumps({
            "topic": topic,
            "trend_score": round(score, 2),
            "timing_recommendation": timing,
            "urgency_level": urgency
        }, indent=2)
    except Exception as e:
        return f"Error getting timing recommendation: {e}"

@mcp.tool()
def compare_topic_trends(topics: list) -> str:
    """Compare trend scores for multiple topics"""
    try:
        if isinstance(topics, str):
            import ast
            topics = ast.literal_eval(topics)

        comparisons = [
            {"topic": t, "score": round(get_trend_score_with_fallback(t), 2)}
            for t in topics
        ]
        comparisons.sort(key=lambda x: x["score"], reverse=True)

        return json.dumps({
            "topic_comparison": comparisons,
            "top_topic": comparisons[0]["topic"] if comparisons else None,
            "score_range": {
                "highest": comparisons[0]["score"] if comparisons else 0,
                "lowest": comparisons[-1]["score"] if comparisons else 0
            }
        }, indent=2)
    except Exception as e:
        return f"Error comparing topics: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
