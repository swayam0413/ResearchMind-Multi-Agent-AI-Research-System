from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

# ── Tavily client with validation ────────────────────────────────────────────
tavily_key = os.getenv("TAVILY_API_KEY")
if not tavily_key:
    raise ValueError(
        "TAVILY_API_KEY not found in .env file. "
        "Please add: TAVILY_API_KEY=your_key_here"
    )
tavily = TavilyClient(api_key=tavily_key.strip())


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)

        out = []
        for r in results['results']:
            out.append(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
            )

        return "\n----\n".join(out) if out else "No results found for this query."
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:3000]
        return text if text.strip() else "Page returned empty content."
    except requests.exceptions.Timeout:
        return f"Could not scrape URL (timeout after 15s): {url}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP error scraping URL: {e}"
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
