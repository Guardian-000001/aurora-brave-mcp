import os
import httpx

from fastmcp import FastMCP

mcp = FastMCP(
    "Aurora Brave Search",
    instructions=(
        "Provides current web search results using Brave Search. "
        "Use web_search for recent, current, or web-based information."
    ),
)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


@mcp.tool
async def web_search(query: str, count: int = 5) -> str:
    """Search the public web using Brave Search."""

    if not BRAVE_API_KEY:
        return "Error: BRAVE_API_KEY is not configured."

    count = max(1, min(count, 10))

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    params = {
        "q": query,
        "count": count,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        data = response.json()

    results = data.get("web", {}).get("results", [])

    if not results:
        return "No web results were found."

    lines = []

    for i, item in enumerate(results, start=1):
        lines.append(
            f"{i}. {item.get('title', '')}\n"
            f"{item.get('description', '')}\n"
            f"Source: {item.get('url', '')}"
        )

    return "\n\n".join(lines)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port,
    )
