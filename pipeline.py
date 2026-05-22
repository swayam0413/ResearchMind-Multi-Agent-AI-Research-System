from agents import run_search, run_reader, safe_writer_invoke, safe_critic_invoke

def run_research_pipeline(topic: str) -> dict:
    """
    Efficient research pipeline — only 2 API calls total.
    Search & Reader use direct tool calls (0 LLM calls).
    Writer & Critic each use 1 LLM call.
    """
    state = {}

    # Step 1 — Search (NO LLM — direct Tavily)
    print("\n" + "=" * 50)
    print("Step 1 - Searching with Tavily (0 API calls)...")
    print("=" * 50)
    state["search_results"] = run_search(topic)
    print("\nSearch results:", state["search_results"][:300])

    # Step 2 — Reader (NO LLM — direct HTTP scrape)
    print("\n" + "=" * 50)
    print("Step 2 - Scraping top URLs (0 API calls)...")
    print("=" * 50)
    state["scraped_content"] = run_reader(state["search_results"])
    print("\nScraped content:", state["scraped_content"][:300])

    # Step 3 — Writer (1 LLM call)
    print("\n" + "=" * 50)
    print("Step 3 - Writing report (1 API call)...")
    print("=" * 50)
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = safe_writer_invoke({
        "topic": topic,
        "research": research_combined,
    })
    print("\nReport:", state["report"][:300])

    # Step 4 — Critic (1 LLM call)
    print("\n" + "=" * 50)
    print("Step 4 - Critiquing report (1 API call)...")
    print("=" * 50)
    state["feedback"] = safe_critic_invoke({
        "report": state["report"],
    })
    print("\nFeedback:", state["feedback"])

    print("\n" + "=" * 50)
    print("DONE! Total API calls used: 2")
    print("=" * 50)

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)
