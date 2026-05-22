from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
import time

load_dotenv()

# Set API key from .env to environment for Google libraries to find it
google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key

# ── Model config ─────────────────────────────────────────────────────────────
# Using Gemini 3 Flash — no live test on startup to conserve quota
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0,
    max_retries=2,          # low retries to conserve quota
    timeout=120,
)
print("[ResearchMind] Model configured: gemini-3-flash-preview")

# ── Rate limiter ─────────────────────────────────────────────────────────────
_last_call_time = 0
MIN_CALL_INTERVAL = 15  # seconds between API calls (5 RPM = 12s minimum)

def _rate_limit():
    """Wait if needed to stay within RPM limits."""
    global _last_call_time
    now = time.time()
    elapsed = now - _last_call_time
    if elapsed < MIN_CALL_INTERVAL:
        wait_time = MIN_CALL_INTERVAL - elapsed
        print(f"[RateLimit] Waiting {wait_time:.0f}s to stay within RPM limit...")
        time.sleep(wait_time)
    _last_call_time = time.time()


# ── Step 1: Search (NO LLM — direct Tavily call) ────────────────────────────
def run_search(topic: str) -> str:
    """Search the web directly using Tavily. Zero LLM calls."""
    print("[Step 1] Searching with Tavily (no LLM needed)...")
    result = web_search.invoke({"query": topic})
    return result


# ── Step 2: Reader (NO LLM — direct HTTP scrape) ─────────────────────────────
def run_reader(search_results: str) -> str:
    """Extract URLs from search results and scrape top ones. Zero LLM calls."""
    print("[Step 2] Scraping URLs (no LLM needed)...")
    import re
    urls = re.findall(r'URL:\s*(https?://[^\s]+)', search_results)

    if not urls:
        # fallback: try to find any URLs
        urls = re.findall(r'https?://[^\s\)\"\']+', search_results)

    scraped = []
    for url in urls[:2]:  # scrape top 2 URLs max to save time
        print(f"  Scraping: {url}")
        content = scrape_url.invoke({"url": url})
        if content and "Could not" not in content and "error" not in content.lower():
            scraped.append(content)

    return "\n\n---\n\n".join(scraped) if scraped else "No content could be scraped from the URLs."


# ── Retry wrapper (conservative) ─────────────────────────────────────────────
def _log_retry(retry_state):
    print(f"[Retry {retry_state.attempt_number}/3] Waiting before next attempt...")

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=3, min=15, max=90),  # longer waits to respect limits
    stop=stop_after_attempt(3),                           # fewer retries to save quota
    reraise=True,
    before_sleep=_log_retry,
)
def _safe_llm_call(chain, inputs: dict):
    """Single LLM call with rate limiting and retry."""
    _rate_limit()
    return chain.invoke(inputs)


# ── Step 3: Writer chain (1 LLM call) ────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
Topic: {topic}
Research Gathered:
{research}
Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)
Be detailed, factual and professional."""),
])
writer_chain = writer_prompt | llm | StrOutputParser()


# ── Step 4: Critic chain (1 LLM call) ────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.
Report:
{report}
Respond in this exact format:
Score: X/10
Strengths:
- ...
- ...
Areas to Improve:
- ...
- ...
One line verdict:
..."""),
])
critic_chain = critic_prompt | llm | StrOutputParser()


# ── Public API ────────────────────────────────────────────────────────────────
def safe_writer_invoke(inputs: dict) -> str:
    """Write report — 1 LLM call with rate limiting."""
    return _safe_llm_call(writer_chain, inputs)

def safe_critic_invoke(inputs: dict) -> str:
    """Critique report — 1 LLM call with rate limiting."""
    return _safe_llm_call(critic_chain, inputs)