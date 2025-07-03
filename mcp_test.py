from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import RunContext
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.gemini import GeminiModel
from dotenv import load_dotenv
import os


load_dotenv()

google_api_key=os.getenv('google_api_key')
tavily_api_key=os.getenv('tavily_key')

llm=GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=google_api_key))

server = MCPServerStdio('npx', [ '-y','@modelcontextprotocol/server-memory'])  
agent = Agent(llm, mcp_servers=[server])
async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('what tools are available?')
        while True:
            print(f'\n{result.data}')
            user_input = input('Enter a prompt: ')
            result = await agent.run(user_input)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())