from contextlib import AsyncExitStack
from typing import Optional

from mcp import StdioServerParameters, stdio_client, ClientSession
import asyncio


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command='uv',
            args=['run', 'file_system.py'],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write))

        await self.session.initialize()

async def main():
    client = MCPClient()
    await client.connect_to_server()
    tool_name = "list_dir"
    tool_args = {"path": r"C:\Users\doppel\Desktop"}  # dict, not string
    result = await client.session.call_tool(tool_name, tool_args)
    print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")
    print(result)
    await client.exit_stack.aclose()

asyncio.run(main())
