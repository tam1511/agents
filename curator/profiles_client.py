# profiles_client.py
import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from agents import FunctionTool
import json

# Point to your profiles_server.py
params = StdioServerParameters(command="python", args=["profiles_server.py"], env=None)


# ---- Tool Management ----
async def list_profiles_tools():
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return tools_result.tools


async def call_profiles_tool(tool_name, tool_args):
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result


# ---- Resource Readers ----
async def read_content_account(name):
    """Read a content account resource from MCP server"""
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.read_resource(f"content-account://{name}")
            return result.contents[0].text


async def read_content_strategy(name):
    """Read a content strategy resource from MCP server"""
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.read_resource(f"content-strategy://{name}")
            return result.contents[0].text


# ---- Convert to OpenAI-compatible tools ----
async def get_profiles_tools_openai():
    """Return profiles tools in OpenAI FunctionTool format"""
    openai_tools = []
    for tool in await list_profiles_tools():
        schema = {**tool.inputSchema, "additionalProperties": False}
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_profiles_tool(toolname, json.loads(args))
        )
        openai_tools.append(openai_tool)
    return openai_tools
