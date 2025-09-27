from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

server_params = StdioServerParameters(
    command='uv',
    args=['run','web_search.py']
)

async def main():
    async with stdio_client(server_params) as (stdio,write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()
            response = await session.list_tools()
            print(response)

            response = await session.call_tool('web_search',{'query' : 'ping'})
            print(response)

