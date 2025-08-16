#!/usr/bin/env python3
"""
Generate demo data for immediate dashboard testing
"""
from profiles import ContentAccount
from datetime import datetime, timedelta
import random

# Sample topics by curator focus
SAMPLE_TOPICS = {
    "Alex": [
        "GPT-4 Breakthrough in Reasoning",
        "New Neural Architecture from DeepMind", 
        "Anthropic's Constitutional AI Research",
        "Meta's Latest LLM Advances",
        "OpenAI's Multimodal Capabilities",
        "Google's PaLM 2 Technical Details",
        "Transformer Architecture Evolution",
        "AI Benchmark Records Broken"
    ],
    "Sam": [
        "ChatGPT Plugins for Business",
        "Claude for Code Generation",
        "Midjourney v5 Features",
        "AI Writing Tools Comparison", 
        "Automated Email Marketing with AI",
        "AI-Powered Customer Service Bots",
        "No-Code AI Tool Tutorial",
        "ROI Analysis of AI Implementation"
    ],
    "Timi": [
        "EU AI Act Latest Updates",
        "AI Bias in Hiring Systems",
        "Privacy Concerns with ChatGPT",
        "Ethical AI Development Guidelines",
        "AI Safety Research Priorities",
        "Regulation vs Innovation Balance",
        "AI Accountability Frameworks",
        "Social Impact of Automation"
    ]
}

PLATFORMS = ["blog", "twitter", "linkedin", "newsletter"]
CONTENT_TYPES = ["article", "post", "thread", "summary", "analysis", "tutorial"]

def generate_mock_content_history(account: ContentAccount, num_pieces: int = 15):
    """Generate mock content history for a curator"""
    topics = SAMPLE_TOPICS.get(account.name.capitalize(), SAMPLE_TOPICS["Alex"])
    
    # Clear existing content
    account.content_history = []
    account.platform_stats = {
        "blog": {"posts": 0, "total_engagement": 0.0},
        "twitter": {"posts": 0, "total_engagement": 0.0},
        "linkedin": {"posts": 0, "total_engagement": 0.0},
        "newsletter": {"posts": 0, "total_engagement": 0.0}
    }
    account.topic_coverage = {}
    account.engagement_time_series = []
    
    # Generate content over the last 30 days
    for i in range(num_pieces):
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = (datetime.now() - timedelta(days=days_ago, hours=hours_ago))
        
        # Random topic and platform
        topic = random.choice(topics)
        platform = random.choice(PLATFORMS)
        content_type = random.choice(CONTENT_TYPES)
        
        # Generate realistic rationale
        rationales = [
            f"High trend score for {topic} topic",
            f"Strategic fit for {platform} audience",
            f"Following up on previous {topic} content",
            f"Capitalizing on trending discussions",
            f"Educational value for target audience"
        ]
        rationale = random.choice(rationales)
        
        try:
            # Use the actual content creation method
            account.create_content(
                topic=topic,
                platform=platform, 
                content_type=content_type,
                rationale=rationale
            )
            
            # Backdate the timestamp
            if account.content_history:
                account.content_history[-1].timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        except ValueError:
            # If out of credits, add more
            account.add_credits(10)
            try:
                account.create_content(topic, platform, content_type, rationale)
                if account.content_history:
                    account.content_history[-1].timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
    
    # Generate engagement time series
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        total_engagement = sum(c.engagement_score for c in account.content_history 
                             if datetime.strptime(c.timestamp, "%Y-%m-%d %H:%M:%S") <= date)
        account.engagement_time_series.append((
            date.strftime("%Y-%m-%d %H:%M:%S"), 
            total_engagement
        ))
    
    account.save()
    return account

def generate_all_demo_data():
    """Generate demo data for all curators"""
    curators = ["Alex", "Sam", "Timi"]
    
    print("🎭 Generating demo data for curators...")
    
    for name in curators:
        print(f"📝 Creating mock data for {name}...")
        account = ContentAccount.get(name)
        
        # Generate different amounts of content
        content_amounts = {"Alex": 12, "Sam": 18, "Timi": 10}
        generate_mock_content_history(account, content_amounts.get(name, 15))
        
        print(f"✅ {name}: {len(account.content_history)} pieces of content")
        print(f"   Total engagement: {account.calculate_total_engagement():.1f}")
        print(f"   Credits remaining: {account.credits}")
    
    print("🎉 Demo data generation complete!")
    print("🎯 Dashboard should now show rich sample data")

def add_recent_activity():
    """Add some very recent activity for live feel"""
    print("⚡ Adding recent activity...")
    
    curators = ["Alex", "Sam", "Timi"] 
    recent_topics = {
        "Alex": ["OpenAI's Latest Research", "Anthropic Safety Update"],
        "Sam": ["New ChatGPT Features", "AI Productivity Hacks"],
        "Timi": ["AI Regulation News", "Ethics in AI Development"]
    }
    
    for name in curators:
        account = ContentAccount.get(name)
        topics = recent_topics[name]
        
        # Add 1-2 very recent pieces
        for topic in topics[:2]:
            try:
                account.create_content(
                    topic=topic,
                    platform=random.choice(["twitter", "linkedin"]),
                    content_type="post",
                    rationale="Breaking news and trending topic"
                )
            except ValueError:
                account.add_credits(5)
                try:
                    account.create_content(topic, "twitter", "post", "Breaking news")
                except:
                    pass
    
    print("✅ Recent activity added")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "recent":
        add_recent_activity()
    else:
        generate_all_demo_data()
        add_recent_activity()