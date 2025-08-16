from enum import Enum

css = """
.dataframe-fix table {
    font-size: 10px !important;
    line-height: 1.2 !important;
}
.dataframe-fix th {
    font-size: 11px !important;
    padding: 2px 4px !important;
    background-color: #f0f0f0 !important;
}
.dataframe-fix td {
    padding: 2px 4px !important;
    max-width: 120px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}
.dataframe-fix-small table {
    font-size: 12px !important;
}
.dataframe-fix-small th {
    font-size: 12px !important;
    padding: 4px 6px !important;
    background-color: #f8f9fa !important;
}
.dataframe-fix-small td {
    padding: 4px 6px !important;
}
.curator-card {
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    margin: 4px !important;
    padding: 16px !important;
}
.engagement-metric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 6px !important;
    padding: 12px !important;
    color: white !important;
    text-align: center !important;
    margin: 4px !important;
}
.platform-badge {
    display: inline-block !important;
    background-color: #e3f2fd !important;
    color: #1976d2 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 10px !important;
    margin: 2px !important;
}
.content-log {
    font-family: 'Courier New', monospace !important;
    font-size: 11px !important;
    background-color: #f8f9fa !important;
    padding: 8px !important;
    border-radius: 4px !important;
    height: 250px !important;
    overflow-y: auto !important;
}
"""

js = """
function refresh() {
    return "";
}
"""

class Color(Enum):
    WHITE = "#ffffff"
    BLACK = "#000000" 
    CYAN = "#00ffff"
    GREEN = "#00ff00"
    YELLOW = "#ffff00"
    MAGENTA = "#ff00ff"
    RED = "#ff0000"
    BLUE = "#0000ff"
    ORANGE = "#ffa500"
    PURPLE = "#800080"
    GRAY = "#808080"

content_log_mapper = {
    "trace": Color.WHITE,
    "agent": Color.CYAN,
    "function": Color.GREEN,
    "generation": Color.YELLOW,
    "response": Color.MAGENTA,
    "content": Color.BLUE,       
    "research": Color.ORANGE,   
    "analysis": Color.PURPLE,   
    "strategy": Color.RED,      
    "engagement": Color.GREEN,  
}

def format_engagement_score(score: float) -> str:
    """Format engagement score for display"""
    if score >= 1000:
        return f"{score/1000:.1f}K"
    elif score >= 100:
        return f"{score:.0f}"
    else:
        return f"{score:.1f}"

def format_credits(credits: float) -> str:
    """Format credits for display"""
    return f"{credits:.0f}"

def get_engagement_color(score: float) -> str:
    """Get color based on engagement score"""
    if score >= 500:
        return "#22c55e"  
    elif score >= 200:
        return "#3b82f6"  
    elif score >= 50:
        return "#f59e0b"  
    else:
        return "#ef4444"  

def get_platform_icon(platform: str) -> str:
    """Get emoji icon for platform"""
    icons = {
        "twitter": "🐦",
        "linkedin": "💼", 
        "blog": "📝",
        "newsletter": "📧",
        "youtube": "🎥",
        "reddit": "🤖",
        "medium": "📖"
    }
    return icons.get(platform.lower(), "📱")

def truncate_content(text: str, max_length: int = 100) -> str:
    """Truncate text for display"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_trend_score(score: float) -> str:
    """Format trend score with color coding"""
    if score >= 70:
        return f"🔥 {score:.1f}"  
    elif score >= 50:
        return f"📈 {score:.1f}"  
    elif score >= 30:
        return f"📊 {score:.1f}"  
    else:
        return f"📉 {score:.1f}" 

def get_content_type_emoji(content_type: str) -> str:
    """Get emoji for content type"""
    emojis = {
        "article": "📄",
        "post": "💬",
        "thread": "🧵",
        "summary": "📋",
        "analysis": "📊",
        "tutorial": "🎓",
        "news": "📰",
        "review": "⭐",
        "guide": "🗺️",
        "promoted_post": "📢"
    }
    return emojis.get(content_type.lower(), "📝")

def calculate_content_velocity(content_count: int, days: int) -> float:
    """Calculate content creation velocity (posts per day)"""
    if days <= 0:
        return 0.0
    return content_count / days

def get_performance_indicator(current_value: float, previous_value: float) -> str:
    """Get performance indicator arrow"""
    if current_value > previous_value:
        return "📈"
    elif current_value < previous_value:
        return "📉"
    else:
        return "➡️"

def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as time ago"""
    from datetime import datetime
    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    except:
        return timestamp_str