from agent import MCP_Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.anthropic import AnthropicModel
from dotenv import load_dotenv
import os
load_dotenv()

llms={'mcp_llm1':OpenAIModel('gpt-4.1-mini',provider=OpenAIProvider(api_key=os.getenv('openai_api_key'))),
      'mcp_llm2':GoogleModel('gemini-2.5-flash', provider=GoogleProvider(api_key=os.getenv('google_api_key'))),
      'mcp_llm3':AnthropicModel('claude-3-5-sonnet-latest', provider=AnthropicProvider(api_key=os.getenv('anthropic_api_key')))}

api_keys={'openai_api_key':os.getenv('openai_api_key')}
http_mcp_server_url1={'url':os.getenv('mcp_server'), 'name': 'mcp_server_1', 'type': 'http', 'headers': None}
http_mcp_server_url2={'url':'https://mcp.notion.com/mcp', 'name': 'mcp_server_2', 'type': 'http', 'headers':''}
stdio_mcp_server_command={'command': 'npx', 'args': ["-y", "mcp-remote", "https://mcp.notion.com/sse"], 'env':{
        "OPENAPI_MCP_HEADERS": ''
      }}



agent=MCP_Agent(llm=llms['mcp_llm3'], api_keys=api_keys,mpc_stdio_commands=[stdio_mcp_server_command])


async def main():
    print(await agent.connect())
    while True:
        result = await agent.chat('what tools are available?')
        print(result)
        user_input = input('Enter a prompt: ')
        result = await agent.chat(user_input)
        print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
