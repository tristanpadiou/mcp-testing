from agent import MCP_Agent
from dotenv import load_dotenv
import os
load_dotenv()

api_keys={'openai_api_key':os.getenv('openai_api_key')}
http_mcp_server_url={'url':os.getenv('mcp_server'), 'name': 'mcp_server_1', 'type': 'http', 'bearer_token': None}
stdio_mcp_server_command={'command': 'npx', 'args': ['-y', '@modelcontextprotocol/server-memory']}

agent=MCP_Agent(api_keys=api_keys, mpc_server_urls=[http_mcp_server_url], mpc_stdio_commands=[stdio_mcp_server_command])

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
