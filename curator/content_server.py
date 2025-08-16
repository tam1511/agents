#!/usr/bin/env python3
"""MCP Server for Content Publishing and Social Media Management"""

from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Create the MCP server
mcp = FastMCP("Content Publishing Server")

# Mock social media APIs
class MockSocialMediaAPI:
    def __init__(self, platform: str):
        self.platform = platform
        self.posts = []
    
    def post_content(self, content: str, content_type: str = "text") -> dict:
        post_id = f"{self.platform}_{len(self.posts) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        post = {
            "id": post_id,
            "platform": self.platform,
            "content": content,
            "content_type": content_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "published",
            "engagement": {
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0
            }
        }
        self.posts.append(post)
        return post

# Initialize mock APIs
twitter_api = MockSocialMediaAPI("twitter")
linkedin_api = MockSocialMediaAPI("linkedin")
blog_api = MockSocialMediaAPI("blog")
newsletter_api = MockSocialMediaAPI("newsletter")

platform_apis = {
    "twitter": twitter_api,
    "linkedin": linkedin_api,
    "blog": blog_api,
    "newsletter": newsletter_api
}

@mcp.tool()
def publish_to_twitter(content: str, content_type: str = "post") -> str:
    """Publish content to Twitter"""
    try:
        # Validate content length for Twitter
        if len(content) > 280:
            return json.dumps({
                "error": "Content too long for Twitter",
                "max_length": 280,
                "current_length": len(content)
            })
        
        result = twitter_api.post_content(content, content_type)
        return json.dumps({
            "success": True,
            "platform": "twitter",
            "post_id": result["id"],
            "published_at": result["timestamp"],
            "content_preview": content[:50] + "..." if len(content) > 50 else content
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to publish to Twitter: {e}"})

@mcp.tool()
def publish_to_linkedin(content: str, content_type: str = "post") -> str:
    """Publish content to LinkedIn"""
    try:
        # Validate content length for LinkedIn
        if len(content) > 3000:
            return json.dumps({
                "error": "Content too long for LinkedIn",
                "max_length": 3000,
                "current_length": len(content)
            })
        
        result = linkedin_api.post_content(content, content_type)
        return json.dumps({
            "success": True,
            "platform": "linkedin",
            "post_id": result["id"],
            "published_at": result["timestamp"],
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to publish to LinkedIn: {e}"})

@mcp.tool()
def publish_to_blog(title: str, content: str, content_type: str = "article") -> str:
    """Publish content to blog"""
    try:
        full_content = f"# {title}\n\n{content}"
        result = blog_api.post_content(full_content, content_type)
        
        return json.dumps({
            "success": True,
            "platform": "blog",
            "post_id": result["id"],
            "published_at": result["timestamp"],
            "title": title,
            "content_length": len(content),
            "url": f"https://example-blog.com/posts/{result['id']}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to publish to blog: {e}"})

@mcp.tool()
def publish_to_newsletter(subject: str, content: str, content_type: str = "newsletter") -> str:
    """Publish content to newsletter"""
    try:
        full_content = f"Subject: {subject}\n\n{content}"
        result = newsletter_api.post_content(full_content, content_type)
        
        return json.dumps({
            "success": True,
            "platform": "newsletter",
            "post_id": result["id"],
            "published_at": result["timestamp"],
            "subject": subject,
            "content_length": len(content),
            "estimated_read_time": max(1, len(content.split()) // 200)  # 200 words per minute
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to publish to newsletter: {e}"})

@mcp.tool()
def get_platform_guidelines(platform: str) -> str:
    """Get content guidelines and best practices for a platform"""
    guidelines = {
        "twitter": {
            "max_length": 280,
            "optimal_length": "100-250 characters",
            "best_practices": [
                "Use hashtags (1-2 max)",
                "Include engaging visuals when possible",
                "Ask questions to encourage engagement",
                "Post at optimal times (9-10 AM, 7-9 PM)",
                "Use threads for longer content"
            ],
            "content_types": ["post", "thread", "quick_take", "news_commentary"]
        },
        "linkedin": {
            "max_length": 3000,
            "optimal_length": "150-300 words",
            "best_practices": [
                "Start with a compelling hook",
                "Share professional insights",
                "Use line breaks for readability",
                "Include a call-to-action",
                "Tag relevant people/companies sparingly"
            ],
            "content_types": ["professional_insight", "industry_analysis", "thought_leadership"]
        },
        "blog": {
            "max_length": "No strict limit",
            "optimal_length": "1500-2500 words",
            "best_practices": [
                "Use clear headings and subheadings",
                "Include introduction and conclusion",
                "Add relevant images/diagrams",
                "Optimize for SEO",
                "Include internal/external links"
            ],
            "content_types": ["article", "tutorial", "analysis", "review", "guide"]
        },
        "newsletter": {
            "max_length": "No strict limit",
            "optimal_length": "800-1500 words",
            "best_practices": [
                "Compelling subject line",
                "Personal tone and voice",
                "Scannable format with sections",
                "Clear call-to-action",
                "Consistent sending schedule"
            ],
            "content_types": ["weekly_roundup", "curated_summary", "deep_dive", "news_digest"]
        }
    }
    
    platform_guide = guidelines.get(platform.lower())
    if not platform_guide:
        return json.dumps({"error": f"No guidelines available for platform: {platform}"})
    
    return json.dumps({
        "platform": platform,
        "guidelines": platform_guide
    }, indent=2)

@mcp.tool()
def get_publishing_history(platform: str = "all", limit: int = 10) -> str:
    """Get publishing history for a platform or all platforms"""
    try:
        all_posts = []
        
        if platform.lower() == "all":
            for api in platform_apis.values():
                all_posts.extend(api.posts)
        elif platform.lower() in platform_apis:
            all_posts = platform_apis[platform.lower()].posts
        else:
            return json.dumps({"error": f"Unknown platform: {platform}"})
        
        # Sort by timestamp (most recent first)
        all_posts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        recent_posts = all_posts[:limit]
        
        return json.dumps({
            "total_posts": len(all_posts),
            "returned_posts": len(recent_posts),
            "posts": recent_posts
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get publishing history: {e}"})

@mcp.tool()
def schedule_content(platform: str, content: str, scheduled_time: str, content_type: str = "post") -> str:
    """Schedule content for future publishing"""
    try:
        # In a real implementation, this would integrate with scheduling services
        scheduled_post = {
            "id": f"scheduled_{platform}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "platform": platform,
            "content": content,
            "content_type": content_type,
            "scheduled_for": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps({
            "success": True,
            "message": "Content scheduled successfully",
            "schedule_details": scheduled_post
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to schedule content: {e}"})

@mcp.tool()
def get_content_performance(post_id: str) -> str:
    """Get performance metrics for published content"""
    try:
        # Search for the post across all platforms
        for platform, api in platform_apis.items():
            for post in api.posts:
                if post["id"] == post_id:
                    # Mock engagement data (in real implementation, fetch from APIs)
                    import random
                    post["engagement"] = {
                        "views": random.randint(50, 5000),
                        "likes": random.randint(5, 500),
                        "shares": random.randint(1, 100),
                        "comments": random.randint(0, 50)
                    }
                    
                    return json.dumps({
                        "post_id": post_id,
                        "platform": platform,
                        "published_at": post["timestamp"],
                        "engagement": post["engagement"],
                        "content_preview": post["content"][:100] + "..."
                    }, indent=2)
        
        return json.dumps({"error": f"Post not found: {post_id}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get content performance: {e}"})

@mcp.tool()
def optimize_content_for_platform(content: str, source_platform: str, target_platform: str) -> str:
    """Optimize content for a different platform"""
    try:
        # Get platform guidelines
        guidelines = get_platform_guidelines(target_platform)
        target_info = json.loads(guidelines)["guidelines"]
        
        # Basic optimization logic
        optimized_content = content
        optimization_notes = []
        
        if target_platform.lower() == "twitter":
            if len(content) > 280:
                optimized_content = content[:277] + "..."
                optimization_notes.append("Truncated to fit Twitter character limit")
        
        elif target_platform.lower() == "linkedin":
            if len(content) < 150:
                optimization_notes.append("Consider expanding content for LinkedIn audience")
            # Add professional tone suggestions
            optimization_notes.append("Consider adding professional insights or industry context")
        
        elif target_platform.lower() == "blog":
            optimization_notes.append("Consider adding headings, images, and expanding with more details")
            
        return json.dumps({
            "source_platform": source_platform,
            "target_platform": target_platform,
            "original_length": len(content),
            "optimized_content": optimized_content,
            "optimized_length": len(optimized_content),
            "optimization_notes": optimization_notes,
            "platform_guidelines": target_info
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to optimize content: {e}"})

if __name__ == "__main__":
    mcp.run(transport='stdio')