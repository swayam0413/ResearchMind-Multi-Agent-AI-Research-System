# 🔬 ResearchMind — Multi-Agent AI Research System

> Four specialized AI agents that collaborate to search, scrape, write, and critique research reports on any topic — using only **2 LLM API calls** per query.

---

## 📌 Overview

ResearchMind is a LangChain-powered multi-agent pipeline with a Streamlit UI. You enter a topic, and four agents handle the rest:

| Step | Agent | LLM Calls | What it does |
|------|-------|-----------|--------------|
| 01 | **Search Agent** | 0 | Searches the web via Tavily API |
| 02 | **Reader Agent** | 0 | Scrapes top URLs for deep content |
| 03 | **Writer Chain** | 1 | Drafts a structured research report |
| 04 | **Critic Chain** | 1 | Reviews and scores the report |

**Total LLM calls per query: 2** — designed to stay within free-tier API limits.

---

## 🗂️ Project Structure

```
ResearchMind/
├── app.py            # Streamlit UI
├── agents.py         # LLM model setup, writer & critic chains, rate limiter
├── pipeline.py       # Orchestrates the 4-step research pipeline
├── tools.py          # Tavily web search & URL scraper tools
├── .env              # API keys (not committed to git)
└── REQUIREMENT.TXT   # Python dependencies
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/researchmind.git
cd researchmind
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r REQUIREMENT.TXT
```

### 4. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

- **Gemini API key** → [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Tavily API key** → [Tavily](https://tavily.com) (free tier available)

---

## 🚀 Running the App

### Streamlit UI (recommended)

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Command Line

```bash
python pipeline.py
```

You'll be prompted to enter a research topic.

---

## 🧠 How It Works

```
User Input (topic)
       │
       ▼
 [Search Agent] ──── Tavily API ──── Web search results (titles, URLs, snippets)
       │
       ▼
 [Reader Agent] ──── HTTP scrape ─── Deep content from top 2 URLs
       │
       ▼
 [Writer Chain] ──── Gemini LLM ──── Structured research report (Intro → Findings → Conclusion → Sources)
       │
       ▼
 [Critic Chain] ──── Gemini LLM ──── Score, strengths, areas to improve, one-line verdict
```

The Search and Reader agents make **zero LLM calls** — they call external APIs and HTTP directly, conserving your quota entirely for the writing and critique steps.

---

## 📄 Report Format

The Writer agent produces reports in this structure:

- **Introduction** — Context and overview of the topic
- **Key Findings** — Minimum 3 well-explained, factual points
- **Conclusion** — Summary and takeaways
- **Sources** — All URLs discovered during research

Reports can be downloaded as `.md` files directly from the UI.

---

## 🧐 Critic Feedback Format

```
Score: X/10
Strengths:
- ...
Areas to Improve:
- ...
One line verdict:
...
```

---

## 🛡️ Rate Limiting & Retry Logic

The app includes built-in safeguards for free-tier API limits:

- **15-second minimum** between LLM calls (respects 5 RPM limit)
- **Exponential backoff** retry: waits 15s → 30s → 90s on failures
- **Max 3 retries** per call to conserve daily quota
- Friendly error messages for 429 (rate limit) and 503 (overload) responses

---

## 🔧 Model Configuration

The app uses **Gemini Flash** (`gemini-3-flash-preview`) by default. To switch models, edit `agents.py`:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",   # change model here
    temperature=0,
    max_retries=2,
    timeout=120,
)
```

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `langchain-google-genai` | Gemini LLM integration |
| `tavily-python` | Web search API |
| `beautifulsoup4` | HTML scraping & parsing |
| `streamlit` | Web UI |
| `tenacity` | Retry logic with backoff |
| `python-dotenv` | Environment variable management |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push and open a Pull Request

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  <sub>ResearchMind · Powered by LangChain · Built with Streamlit · Gemini AI</sub>
</div>
