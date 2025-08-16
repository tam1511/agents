from contextlib import AsyncExitStack
from profiles_client import read_content_account, read_content_strategy
from tracers import make_trace_id
from agents import Agent, Tool, Runner, OpenAIChatCompletionsModel, trace
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import json
from agents.mcp import MCPServerStdio
from curator_templates import (
    researcher_instructions,
    curator_instructions,
    content_creation_message,
    content_review_message,
    trending_topics_message,
    content_analytics_message,
    research_tool,
)
from mcp_servers import curator_mcp_server_params, researcher_mcp_server_params

load_dotenv(override=True)

# API clients 
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
# Base URLs
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

MAX_TURNS = 30

# Clients
print("GOOGLE_API_KEY:", "SET" if google_api_key else "NOT SET")
print("GROQ_API_KEY:", "SET" if groq_api_key else "NOT SET")

gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)

def get_model(model_name: str):
    print(f"[DEBUG] get_model called with: {model_name}")

    if "groq" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=groq_client)
    elif "gemini" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=gemini_client)
    elif model_name.startswith("gpt-"):
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return OpenAIChatCompletionsModel(model=model_name, openai_client=openai_client)
    else:
        raise ValueError(f"Model {model_name} is not supported.")



async def get_ai_researcher(mcp_servers, model_name) -> Agent:
    researcher = Agent(
        name="AI_Trends_Researcher",
        instructions=researcher_instructions(),
        model=get_model(model_name),
        mcp_servers=mcp_servers,
    )
    return researcher


async def get_ai_researcher_tool(mcp_servers, model_name) -> Tool:
    researcher = await get_ai_researcher(mcp_servers, model_name)
    return researcher.as_tool(tool_name="AI_Researcher", tool_description=research_tool())


class ContentCurator:
    def __init__(self, name: str, model_name="gpt-4o-mini"):
        self.name = name
        self.agent = None
        self.model_name = model_name
        self.mode = "content_creation"

    async def create_agent(self, curator_mcp_servers, researcher_mcp_servers) -> Agent:
        research_tool = await get_ai_researcher_tool(researcher_mcp_servers, self.model_name)
        self.agent = Agent(
            name=self.name,
            instructions=curator_instructions(self.name),
            model=get_model(self.model_name),
            tools=[research_tool],
            mcp_servers=curator_mcp_servers,
        )
        return self.agent

    async def get_content_account_report(self) -> str:
        account = await read_content_account(self.name)
        account_json = json.loads(account)
        account_json.pop("engagement_time_series", None)
        return json.dumps(account_json, indent=2)

    async def run_content_creation(self, curator_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(curator_mcp_servers, researcher_mcp_servers)
        account = await self.get_content_account_report()
        strategy = await read_content_strategy(self.name)
        message = content_creation_message(self.name, strategy, account)
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    async def run_content_review(self, curator_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(curator_mcp_servers, researcher_mcp_servers)
        account = await self.get_content_account_report()
        strategy = await read_content_strategy(self.name)
        message = content_review_message(self.name, strategy, account)
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    async def run_trending_research(self, curator_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(curator_mcp_servers, researcher_mcp_servers)
        strategy = await read_content_strategy(self.name)
        message = trending_topics_message(self.name, strategy)
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    async def run_analytics(self, curator_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(curator_mcp_servers, researcher_mcp_servers)
        account = await self.get_content_account_report()
        message = content_analytics_message(self.name, account)
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    async def run_agent(self, curator_mcp_servers, researcher_mcp_servers):
        if self.mode == "content_creation":
            await self.run_content_creation(curator_mcp_servers, researcher_mcp_servers)
        elif self.mode == "review":
            await self.run_content_review(curator_mcp_servers, researcher_mcp_servers)
        elif self.mode == "research_only":
            await self.run_trending_research(curator_mcp_servers, researcher_mcp_servers)
        elif self.mode == "analytics":
            await self.run_analytics(curator_mcp_servers, researcher_mcp_servers)
        else:
            await self.run_content_creation(curator_mcp_servers, researcher_mcp_servers)

    async def run_with_mcp_servers(self):
        async with AsyncExitStack() as stack:
            curator_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds=120)
                )
                for params in curator_mcp_server_params
            ]
            async with AsyncExitStack() as stack:
                researcher_mcp_servers = [
                    await stack.enter_async_context(
                        MCPServerStdio(params, client_session_timeout_seconds=120)
                    )
                    for params in researcher_mcp_server_params(self.name)
                ]
                await self.run_agent(curator_mcp_servers, researcher_mcp_servers)

    async def run_with_trace(self):
        trace_name = f"{self.name}-{self.mode}"
        trace_id = make_trace_id(f"{self.name.lower()}")
        with trace(trace_name, trace_id=trace_id):
            await self.run_with_mcp_servers()

    async def run(self):
        try:
            await self.run_with_trace()
        except Exception as e:
            print(f"Error running content curator {self.name}: {e}")

        mode_cycle = ["content_creation", "review", "research_only", "analytics"]
        current_index = mode_cycle.index(self.mode) if self.mode in mode_cycle else 0
        self.mode = mode_cycle[(current_index + 1) % len(mode_cycle)]

    def set_mode(self, mode: str):
        valid_modes = ["content_creation", "review", "research_only", "analytics"]
        if mode in valid_modes:
            self.mode = mode
        else:
            raise ValueError(f"Invalid mode. Must be one of: {valid_modes}")