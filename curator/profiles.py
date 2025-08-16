from pydantic import BaseModel
import json
from dotenv import load_dotenv
from datetime import datetime
from trends import get_trend_score_with_fallback
from database import write_profile, read_profile, write_log
from typing import List

load_dotenv(override=True)

INITIAL_CREDITS = 100  
CONTENT_COST = 1  
ENGAGEMENT_MULTIPLIER = 10  


class ContentPiece(BaseModel):
    topic: str
    platform: str  
    content_type: str  
    trend_score: float
    timestamp: str
    strategy_rationale: str
    engagement_score: float = 0.0  
    
    def __repr__(self):
        return f"{self.content_type} about {self.topic} on {self.platform} (trend: {self.trend_score:.1f})"


class ContentAccount(BaseModel):
    name: str
    credits: float
    strategy: str
    content_history: List[ContentPiece]
    engagement_time_series: list[tuple[str, float]]
    platform_stats: dict[str, dict]  
    topic_coverage: dict[str, int]  

    @classmethod
    def get(cls, name: str):
        fields = read_profile(name.lower())
        if not fields:
            fields = {
                "name": name.lower(),
                "credits": INITIAL_CREDITS,
                "strategy": "",
                "content_history": [],
                "engagement_time_series": [],
                "platform_stats": {
                    "blog": {"posts": 0, "total_engagement": 0.0},
                    "twitter": {"posts": 0, "total_engagement": 0.0},
                    "linkedin": {"posts": 0, "total_engagement": 0.0},
                    "newsletter": {"posts": 0, "total_engagement": 0.0}
                },
                "topic_coverage": {}
            }
            write_profile(name, fields)
        return cls(**fields)
    
    def save(self):
        write_profile(self.name.lower(), self.model_dump())

    def reset(self, strategy: str):
        self.credits = INITIAL_CREDITS
        self.strategy = strategy
        self.content_history = []
        self.engagement_time_series = []
        self.platform_stats = {
            "blog": {"posts": 0, "total_engagement": 0.0},
            "twitter": {"posts": 0, "total_engagement": 0.0},
            "linkedin": {"posts": 0, "total_engagement": 0.0},
            "newsletter": {"posts": 0, "total_engagement": 0.0}
        }
        self.topic_coverage = {}
        self.save()

    def add_credits(self, amount: float):
        """Add credits to the account (e.g., monthly allocation)"""
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self.credits += amount
        print(f"Added {amount} credits. New balance: {self.credits}")
        self.save()

    def use_credits(self, amount: float):
        """Use credits for content creation"""
        if amount > self.credits:
            raise ValueError("Insufficient credits for content creation.")
        self.credits -= amount
        print(f"Used {amount} credits. Remaining: {self.credits}")
        self.save()

    def create_content(self, topic: str, platform: str, content_type: str, rationale: str) -> str:
        """Create content if sufficient credits are available"""
        if self.credits < CONTENT_COST:
            raise ValueError("Insufficient credits to create content.")
        
        trend_score = get_trend_score_with_fallback(topic)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        
        platform_multipliers = {
            "twitter": 1.2,
            "linkedin": 0.8,
            "blog": 1.5,
            "newsletter": 1.0
        }
        
        base_engagement = trend_score * ENGAGEMENT_MULTIPLIER
        engagement_score = base_engagement * platform_multipliers.get(platform, 1.0)
       
        content_piece = ContentPiece(
            topic=topic,
            platform=platform,
            content_type=content_type,
            trend_score=trend_score,
            timestamp=timestamp,
            strategy_rationale=rationale,
            engagement_score=engagement_score
        )

        self.content_history.append(content_piece)
        self.use_credits(CONTENT_COST)

        if platform not in self.platform_stats:
            self.platform_stats[platform] = {"posts": 0, "total_engagement": 0.0}
        
        self.platform_stats[platform]["posts"] += 1
        self.platform_stats[platform]["total_engagement"] += engagement_score

        self.topic_coverage[topic] = self.topic_coverage.get(topic, 0) + 1
        
        self.save()
        write_log(self.name, "content", f"Created {content_type} about {topic} on {platform}")
        return "Content created successfully. Latest details:\n" + self.report()

    def skip_content(self, topic: str, rationale: str) -> str:
        """Record a decision to skip content creation for a topic"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_log(self.name, "content", f"Skipped content for {topic}: {rationale}")
        return f"Content skipped for {topic}. Rationale: {rationale}"

    def promote_existing_content(self, topic: str, platform: str, rationale: str) -> str:
        """Promote existing content to a new platform"""
 
        existing_content = [c for c in self.content_history if topic.lower() in c.topic.lower()]
        
        if not existing_content:
            raise ValueError(f"No existing content found for topic: {topic}")
        
        if self.credits < CONTENT_COST:
            raise ValueError("Insufficient credits to promote content.")
        
  
        source_content = max(existing_content, key=lambda x: x.trend_score)
        
        return self.create_content(topic, platform, "promoted_post", 
                                 f"Promotion: {rationale}")

    def calculate_total_engagement(self) -> float:
        """Calculate total engagement across all content"""
        return sum(content.engagement_score for content in self.content_history)

    def calculate_engagement_rate(self) -> float:
        """Calculate average engagement per content piece"""
        if not self.content_history:
            return 0.0
        return self.calculate_total_engagement() / len(self.content_history)

    def get_platform_performance(self) -> dict[str, float]:
        """Get engagement performance by platform"""
        performance = {}
        for platform, stats in self.platform_stats.items():
            if stats["posts"] > 0:
                performance[platform] = stats["total_engagement"] / stats["posts"]
            else:
                performance[platform] = 0.0
        return performance

    def get_top_topics(self, limit: int = 5) -> list[tuple[str, int]]:
        """Get most covered topics"""
        sorted_topics = sorted(self.topic_coverage.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:limit]

    def get_content_history(self):
        """Get all content creation history"""
        return [content.model_dump() for content in self.content_history]

    def get_recent_content(self, days: int = 7) -> list[dict]:
        """Get content created in the last N days as plain dicts (JSON-ready)"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        recent_content = [
            content.model_dump()
            for content in self.content_history
            if datetime.strptime(content.timestamp, "%Y-%m-%d %H:%M:%S").timestamp() >= cutoff_date
        ]
        
        return recent_content


    def report(self) -> str:
        """Return a JSON string representing the account"""
        total_engagement = self.calculate_total_engagement()
        engagement_rate = self.calculate_engagement_rate()
        
        self.engagement_time_series.append((
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            total_engagement
        ))
        self.save()
        
        data = self.model_dump()
        data["total_engagement"] = total_engagement
        data["engagement_rate"] = engagement_rate
        data["platform_performance"] = self.get_platform_performance()
        data["top_topics"] = self.get_top_topics()
        data["recent_content_count"] = len(self.get_recent_content())
        
        write_log(self.name, "content_account", "Retrieved account details")
        return json.dumps(data, indent=2)

    def get_strategy(self) -> str:
        """Return the content strategy of the account"""
        write_log(self.name, "content_account", "Retrieved strategy")
        return self.strategy
    
    def change_strategy(self, strategy: str) -> str:
        """Change the content strategy"""
        self.strategy = strategy
        self.save()
        write_log(self.name, "content_account", "Changed strategy")
        return f"Content strategy updated: {strategy}"

    def analyze_performance(self) -> dict:
        """Analyze content performance and provide insights"""
        if not self.content_history:
            return {"message": "No content history to analyze"}

        platform_analysis = {}
        for platform in self.platform_stats:
            stats = self.platform_stats[platform]
            if stats["posts"] > 0:
                avg_engagement = stats["total_engagement"] / stats["posts"]
                platform_analysis[platform] = {
                    "posts": stats["posts"],
                    "total_engagement": stats["total_engagement"],
                    "avg_engagement": avg_engagement
                }

        topic_performance = {}
        for content in self.content_history:
            topic = content.topic
            if topic not in topic_performance:
                topic_performance[topic] = {
                    "count": 0,
                    "total_engagement": 0,
                    "avg_trend_score": 0
                }
            
            topic_performance[topic]["count"] += 1
            topic_performance[topic]["total_engagement"] += content.engagement_score
            topic_performance[topic]["avg_trend_score"] += content.trend_score

        for topic in topic_performance:
            count = topic_performance[topic]["count"]
            topic_performance[topic]["avg_engagement"] = topic_performance[topic]["total_engagement"] / count
            topic_performance[topic]["avg_trend_score"] = topic_performance[topic]["avg_trend_score"] / count
        
        return {
            "total_content": len(self.content_history),
            "total_engagement": self.calculate_total_engagement(),
            "avg_engagement": self.calculate_engagement_rate(),
            "platform_analysis": platform_analysis,
            "topic_performance": topic_performance,
            "credits_remaining": self.credits
        }



if __name__ == "__main__":
    account = ContentAccount.get("AI_Content_Creator")
    account.reset("Focus on trending AI breakthroughs and practical applications")
    

    account.create_content("GPT-4 breakthrough", "blog", "article", 
                          "High trend score and educational value")
    account.create_content("AI ethics debate", "twitter", "thread", 
                          "Engaging topic for social discussion")
    account.create_content("Machine learning tutorial", "linkedin", "post", 
                          "Professional audience interested in AI skills")
    
    print("Account Report:")
    print(account.report())
    
    print("\nPerformance Analysis:")
    analysis = account.analyze_performance()
    print(json.dumps(analysis, indent=2))