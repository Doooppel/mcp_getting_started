import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Optional, Iterable, Any

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from openai.types.chat import ChatCompletionFunctionToolParam, ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam, \
    ChatCompletionFunctionMessageParam
from openai.types.shared_params import FunctionDefinition

load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"),base_url=os.getenv("OPENAI_URL"))

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

    async def process_query(self, query: str) -> str:
        # system prompt to refrain llm else it will respond non-sense
        system_prompt = (
            "You are a helpful assistant."
            "You have the function of online search. "
            "Please MUST call file_system tool to search the Internet content before answering."
            "Please do not lose the user's question information when searching,"
            "and try to maintain the completeness of the question content as much as possible."
            "When there is a date related question in the user's question,"
            "please use the search function directly to search and PROHIBIT inserting specific time."
        )

        messages: list[Any] = [
            ChatCompletionSystemMessageParam(content=system_prompt, role="system"),
            ChatCompletionUserMessageParam(content=query, role="user"),
        ]

        # get all tools info from mcp server
        response = await self.session.list_tools()
        # generate function call params
        available_tools: Iterable[ChatCompletionFunctionToolParam] = [
            ChatCompletionFunctionToolParam(
                type="function",
                function= FunctionDefinition(name=tool.name,description=tool.description,parameters=tool.inputSchema),
            )
            for tool in response.tools
        ]
        # request llm with tools metadata
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools
        )

        # handle response from llm
        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            # if llm indicate to use tool then use the tool
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # execute tool call and parse the tool response.
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")

            function_message = ChatCompletionFunctionMessageParam(content=result.content[0].text,name=tool_name,role="function")
            messages.append(function_message)

            # feed response from tool to llm again to generate final response
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
            )
            return response.choices[0].message.content

        return content.message.content

    async def chat_loop(self):
        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
        client = MCPClient()
        try:
            await client.connect_to_server()
            await client.chat_loop()
        finally:
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
