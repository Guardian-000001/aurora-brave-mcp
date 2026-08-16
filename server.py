import os
import httpx

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Aurora Brave Search")

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


@mcp.tool()
async def web_search(query: str, count: int = 5) -> str:
    """
    Search the public web using Brave Search and return current results.
    Use this tool when the user asks for recent, current, or web-based information.
    """

    if not BRAVE_API_KEY:
        return "Error: BRAVE_API_KEY is not configured."

    count = max(1, min(count, 10))

    url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    params = {
        "q": query,
        "count": count,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    results = data.get("web", {}).get("results", [])

    if not results:
        return "No web results were found."

    output = []

    for i, item in enumerate(results, start=1):
        title = item.get("title", "")
        description = item.get("description", "")
        result_url = item.get("url", "")

        output.append(
            f"{i}. {title}\n"
            f"{description}\n"
            f"Source: {result_url}"
        )

    return "\n\n".join(output)


app = mcp.sse_app()
