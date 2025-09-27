import os

from mcp.server import FastMCP

from gemini_client import GeminiClient

app = FastMCP('web-search')

@app.tool()
async def web_search(query: str) -> str:
    """
    search on web
    :param query: content to be searched
    :return: summary
    """
    client = GeminiClient(api_key=os.getenv("OPENAI_KEY"))
    text = await client.generate_async(query)
    print(text)
    return text

if __name__ == '__main__':
    app.run(transport='stdio')