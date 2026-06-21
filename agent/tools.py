from tavily import TavilyClient
import os
import logging

logger = logging.getLogger(__name__)

def web_search_tool(query: str) -> str:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "No relevant information found."
        combined = "\n\n".join([r["content"] for r in results])
        return combined
    except Exception as e:
        logger.error("Web search failed: %s", e)
        return "Web search failed."

TOOL_REGISTRY = {
    "web_search": {
        "fn": web_search_tool,
        "description": "Search the web for current information not in documents or database",
        "args": ["query"]
    }
}