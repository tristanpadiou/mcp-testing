from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.mcp import MCPServerStdio,MCPServerStreamableHTTP,MCPServerSSE
from dotenv import load_dotenv
import os
load_dotenv()

llms={'mcp_llm1':OpenAIModel('gpt-4.1-mini',provider=OpenAIProvider(api_key=os.getenv('openai_api_key'))),
      'mcp_llm2':GoogleModel('gemini-2.5-flash', provider=GoogleProvider(api_key=os.getenv('google_api_key')))}

api_keys={'openai_api_key':os.getenv('openai_api_key')}
http_mcp_server_url1={'url':'https://mcp.notion.com/sse', 'name': 'mcp_server_1', 'type': 'sse', 'headers': {"Authorization":"Bearer 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","Notion-Version":"2022-06-28"}}
http_mcp_server_url2={'url':'https://mcp.notion.com/mcp', 'name': 'mcp_server_2', 'type': 'http', 'headers':{"Authorization":"Bearer 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","Notion-Version":"2022-06-28"}}
stdio_mcp_server_command={'command': 'npx', 'args': ["-y", "mcp-remote", "https://mcp.notion.com/sse"], 'env':{
        "OPENAPI_MCP_HEADERS": "{\"Authorization\":\"Bearer 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\",\"Notion-Version\":\"2022-06-28\"}"
      }}

import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
    # methods will go here
    async def connect_to_server(self, mpc_server_command: dict):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        command = mpc_server_command['command']
        server_params = StdioServerParameters(
            command=command,
            args=mpc_server_command['args'],
            env=mpc_server_command['env']
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():


    client = MCPClient()
    try:
        await client.connect_to_server(stdio_mcp_server_command)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())


