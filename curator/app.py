import gradio as gr
from util import css, js, content_log_mapper, format_engagement_score, get_engagement_color, get_platform_icon, format_time_ago
import pandas as pd
from content_floor import names, lastnames, short_model_names, focus_areas, curator_colors
import plotly.express as px
import plotly.graph_objects as go
from profiles import ContentAccount
from database import read_log
from datetime import datetime, timedelta


class ContentCurator:
    def __init__(self, name: str, lastname: str, model_name: str, color: str):
        self.name = name
        self.lastname = lastname
        self.model_name = model_name
        self.color = color
        self.account = ContentAccount.get(name)

    def reload(self):
        self.account = ContentAccount.get(self.name)

    def get_title(self) -> str:
        focus = focus_areas[names.index(self.name)]
        return f"""<div style='text-align: center; font-size: 28px; padding: 10px; background: linear-gradient(135deg, {self.color}22, {self.color}11); border-radius: 8px; margin-bottom: 10px;'>
        <strong>{self.name}</strong> <span style='color: #666; font-size: 18px;'>({self.model_name})</span>
        <br><span style='font-size: 16px; color: {self.color};'>{focus}</span>
        <br><span style='font-size: 14px; color: #888;'>{self.lastname}</span>
        </div>"""

    def get_strategy(self) -> str:
        return self.account.get_strategy()

    def get_engagement_time_series_df(self) -> pd.DataFrame:
        """Get engagement over time as DataFrame"""
        if not self.account.engagement_time_series:
            return pd.DataFrame({
                "datetime": [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)],
                "engagement": [0] * 7
            })
        
        df = pd.DataFrame(self.account.engagement_time_series, columns=["datetime", "engagement"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df

    def get_engagement_chart(self):
        """Create engagement over time chart"""
        df = self.get_engagement_time_series_df()
        
        fig = px.line(df, x="datetime", y="engagement", 
                     line_shape="spline",
                     markers=True)
        
        fig.update_traces(
            line_color=self.color,
            marker=dict(size=6, color=self.color),
            fill='tonexty'
        )
        
        margin = dict(l=40, r=20, t=20, b=40)
        fig.update_layout(
            height=280,
            margin=margin,
            xaxis_title=None,
            yaxis_title="Engagement",
            paper_bgcolor="#fafafa",
            plot_bgcolor="white",
            showlegend=False,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor="#eee"),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor="#eee")
        )
        fig.update_xaxes(tickformat="%m/%d", tickangle=45, tickfont=dict(size=10))
        fig.update_yaxes(tickfont=dict(size=10))
        return fig

    def get_platform_performance_chart(self):
        """Create platform performance chart"""
        platform_stats = self.account.platform_stats
        platforms = []
        posts = []
        engagement = []
        
        for platform, stats in platform_stats.items():
            if stats["posts"] > 0:
                platforms.append(f"{get_platform_icon(platform)} {platform.title()}")
                posts.append(stats["posts"])
                engagement.append(stats["total_engagement"])
        
        if not platforms:
            fig = go.Figure()
            fig.add_annotation(text="No content created yet", 
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
            return fig

        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=platforms,
            y=posts,
            name="Posts",
            marker_color=self.color,
            opacity=0.7,
            yaxis="y"
        ))
        
        fig.add_trace(go.Scatter(
            x=platforms,
            y=engagement,
            name="Engagement",
            mode="lines+markers",
            line=dict(color="#ff6b6b", width=3),
            marker=dict(size=8),
            yaxis="y2"
        ))
        
        fig.update_layout(
            height=200,
            margin=dict(l=40, r=40, t=20, b=60),
            yaxis=dict(title="Posts", side="left"),
            yaxis2=dict(title="Engagement", side="right", overlaying="y"),
            showlegend=False,
            paper_bgcolor="#fafafa",
            plot_bgcolor="white",
            xaxis=dict(tickangle=45, tickfont=dict(size=9))
        )
        
        return fig

    def get_content_summary_df(self) -> pd.DataFrame:
        """Get recent content as DataFrame"""
        recent_content = self.account.get_recent_content(7)
        if not recent_content:
            return pd.DataFrame(columns=["Time", "Platform", "Topic", "Type", "Engagement"])

        data = []
        for content in recent_content[:10]: 
            data.append({
                "Time": format_time_ago(content['timestamp']),  # Fix: dict access
                "Platform": f"{get_platform_icon(content['platform'])} {content['platform'].title()}",  # Fix: dict access
                "Topic": content['topic'][:30] + "..." if len(content['topic']) > 30 else content['topic'],  # Fix: dict access
                "Type": content['content_type'].replace("_", " ").title(),  # Fix: dict access
                "Engagement": format_engagement_score(content['engagement_score']),  # Fix: dict access
                "Trend": f"{content['trend_score']:.1f}"  # Fix: dict access
            })
        
        return pd.DataFrame(data)

    def get_topic_coverage_df(self) -> pd.DataFrame:
        """Get top topics as DataFrame"""
        top_topics = self.account.get_top_topics(8)
        if not top_topics:
            return pd.DataFrame(columns=["Topic", "Posts"])

        data = []
        for topic, count in top_topics:
            data.append({
                "Topic": topic[:25] + "..." if len(topic) > 25 else topic,
                "Posts": count
            })
        
        return pd.DataFrame(data)

    def get_performance_metrics(self) -> str:
        """Get key performance metrics as HTML"""
        total_engagement = self.account.calculate_total_engagement()
        total_content = len(self.account.content_history)
        avg_engagement = self.account.calculate_engagement_rate()
        credits = self.account.credits
        
        recent_content = self.account.get_recent_content(7)
        # Fix: access engagement_score from dict instead of object attribute
        recent_engagement = sum(c['engagement_score'] for c in recent_content)
        
        color = get_engagement_color(avg_engagement)
        
        return f"""
        <div style='display: flex; justify-content: space-around; text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, {color}22, {color}11); padding: 12px; border-radius: 8px; margin: 4px; flex: 1;'>
                <div style='font-size: 24px; font-weight: bold; color: {color};'>{total_content}</div>
                <div style='font-size: 12px; color: #666;'>Total Posts</div>
            </div>
            <div style='background: linear-gradient(135deg, #3b82f622, #3b82f611); padding: 12px; border-radius: 8px; margin: 4px; flex: 1;'>
                <div style='font-size: 24px; font-weight: bold; color: #3b82f6;'>{format_engagement_score(total_engagement)}</div>
                <div style='font-size: 12px; color: #666;'>Total Engagement</div>
            </div>
            <div style='background: linear-gradient(135deg, #f59e0b22, #f59e0b11); padding: 12px; border-radius: 8px; margin: 4px; flex: 1;'>
                <div style='font-size: 24px; font-weight: bold; color: #f59e0b;'>{avg_engagement:.1f}</div>
                <div style='font-size: 12px; color: #666;'>Avg Engagement</div>
            </div>
            <div style='background: linear-gradient(135deg, #8b5cf622, #8b5cf611); padding: 12px; border-radius: 8px; margin: 4px; flex: 1;'>
                <div style='font-size: 24px; font-weight: bold; color: #8b5cf6;'>{credits:.0f}</div>
                <div style='font-size: 12px; color: #666;'>Credits</div>
            </div>
        </div>
        """

    def get_logs(self, previous=None) -> str:
        """Get formatted logs"""
        logs = read_log(self.name, last_n=15)
        response = ""
        for log in logs:
            timestamp, log_type, message = log
            color = content_log_mapper.get(log_type, content_log_mapper["trace"]).value
            if len(message) > 100:
                message = message[:97] + "..."
            response += f"<span style='color:{color}; display: block; margin: 2px 0;'><strong>{timestamp}</strong> [{log_type.upper()}] {message}</span>"
        
        response = f"<div class='content-log'>{response}</div>"
        if response != previous:
            return response
        return gr.update()


class ContentCuratorView:
    def __init__(self, curator: ContentCurator):
        self.curator = curator
        self.performance_metrics = None
        self.engagement_chart = None
        self.platform_chart = None
        self.content_table = None
        self.topics_table = None
        self.log = None

    def make_ui(self):
        with gr.Column(elem_classes=["curator-card"]):
            gr.HTML(self.curator.get_title)
            
            with gr.Row():
                self.performance_metrics = gr.HTML(self.curator.get_performance_metrics)

            with gr.Row():
                with gr.Column():
                    self.engagement_chart = gr.Plot(
                        self.curator.get_engagement_chart, 
                        container=True, 
                        show_label=False,
                        label="Engagement Over Time"
                    )
                with gr.Column():
                    self.platform_chart = gr.Plot(
                        self.curator.get_platform_performance_chart,
                        container=True,
                        show_label=False,
                        label="Platform Performance"
                    )

            with gr.Row():
                self.log = gr.HTML(
                    self.curator.get_logs,
                    label="Activity Log"
                )

            with gr.Row():
                with gr.Column():
                    self.content_table = gr.Dataframe(
                        value=self.curator.get_content_summary_df,
                        label="Recent Content",
                        headers=["Time", "Platform", "Topic", "Type", "Engagement", "Trend"],
                        row_count=(6, "dynamic"),
                        col_count=6,
                        max_height=250,
                        elem_classes=["dataframe-fix"],
                    )
                with gr.Column():
                    self.topics_table = gr.Dataframe(
                        value=self.curator.get_topic_coverage_df,
                        label="Top Topics",
                        headers=["Topic", "Posts"],
                        row_count=(6, "dynamic"),
                        col_count=2,
                        max_height=250,
                        elem_classes=["dataframe-fix-small"],
                    )

        refresh_timer = gr.Timer(value=30)  
        refresh_timer.tick(
            fn=self.refresh,
            inputs=[],
            outputs=[
                self.performance_metrics,
                self.engagement_chart,
                self.platform_chart,
                self.content_table,
                self.topics_table,
            ],
            show_progress="hidden",
            queue=False,
        )
        
        log_timer = gr.Timer(value=2)  
        log_timer.tick(
            fn=self.curator.get_logs,
            inputs=[self.log],
            outputs=[self.log],
            show_progress="hidden",
            queue=False,
        )

    def refresh(self):
        """Refresh all curator data"""
        self.curator.reload()
        return (
            self.curator.get_performance_metrics(),
            self.curator.get_engagement_chart(),
            self.curator.get_platform_performance_chart(),
            self.curator.get_content_summary_df(),
            self.curator.get_topic_coverage_df(),
        )


def create_content_ui():
    """Create the main Gradio UI for content curators"""
    
    curators = [
        ContentCurator(name, lastname, model_name, color)
        for name, lastname, model_name, color in zip(names, lastnames, short_model_names, curator_colors)
    ]
    curator_views = [ContentCuratorView(curator) for curator in curators]

    with gr.Blocks(
        title="AI Content Curators",
        css=css,
        js=js,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="gray"),
        fill_width=True
    ) as ui:
        gr.HTML("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 20px;'>
            <h1 style='margin: 0; font-size: 36px;'>🤖 AI Content Curators Dashboard</h1>
            <p style='margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;'>Autonomous AI agents creating and curating trending content</p>
        </div>
        """)

        with gr.Row():
            for curator_view in curator_views:
                curator_view.make_ui()

        gr.HTML("""
        <div style='text-align: center; padding: 15px; color: #666; font-size: 14px; margin-top: 20px;'>
            <p>🚀 Content curators autonomously research trending AI topics and create engaging content across multiple platforms</p>
        </div>
        """)

    return ui


if __name__ == "__main__":
    
    ui = create_content_ui()
    ui.launch(
        inbrowser=True,
        server_name="0.0.0.0",
        server_port=7861,  
        share=False
    )