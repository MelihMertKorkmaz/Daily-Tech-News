# 📰 NewsDigest / Daily Tech News — AI-Powered Daily News Aggregator

A full-stack **Django** web application that automatically collects news articles from RSS feeds, scrapes full article content, and generates concise AI-powered summaries using **Google Gemini**. Browse daily digests through a sleek, dark-mode-ready web interface with a card-based slideshow.

---

## ✨ Features

- **Multi-Category Coverage** — Aggregates news across **Tech** and **World Politics** from configurable RSS sources
- **AI Summarization** — Leverages **Google Gemini (gemini-2.5-flash-lite)** to produce 8–10 sentence summaries per article
- **Full-Text Scraping** — Extracts complete article content and opengraph preview images from source URLs
- **Smart Deduplication** — Filters duplicate articles both at ingestion (cross-source title similarity) and at the AI output stage
- **Interactive UI** — Slideshow-style article viewer with keyboard navigation (← →) and dark/light mode toggle
- **Automated Pipelines** — One-command scripts to fetch + summarize, with Celery integration for scheduled daily runs
- **Date-Based Archives** — Browse summaries for any past date via a clean date-picker homepage

---

## 🏗️ Architecture

```
newsdigest/
├── commands/                # CLI scripts
│   ├── fetch.py             # Fetch articles only
│   ├── summarize.py         # Generate summaries only
│   └── fetch_and_summarize.py  # Full pipeline (fetch → summarize)
├── news/                    # Core Django app
│   ├── models.py            # Article, DailySummary, RSSSource (Tech & Politics)
│   ├── fetch_articles.py    # RSS feed parsing + web scraping
│   ├── summarizer.py        # Gemini AI summarization engine
│   ├── gemini.py            # Gemini API client configuration
│   ├── views.py             # Django views & summary block parser
│   ├── urls.py              # URL routing
│   ├── tasks.py             # Celery periodic tasks
│   ├── templates/news/      # HTML templates (home, daily summary, politics)
│   └── static/news/         # CSS styles & background images
├── technews/                # Django project settings
└── manage.py
```

---

## ⚙️ Tech Stack

| Layer           | Technology                                    |
|-----------------|-----------------------------------------------|
| **Backend**     | Python, Django 5.1                            |
| **AI / LLM**    | Google Gemini API (`gemini-2.5-flash-lite`)   |
| **Data Ingestion** | `feedparser`, `requests`, `BeautifulSoup4` |
| **Task Queue**  | Celery + Redis                                |
| **Database**    | SQLite                                        |
| **Frontend**    | Django Templates, Vanilla CSS, JavaScript     |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Redis (for Celery task scheduling)
- A [Google Gemini API key](https://ai.google.dev/)

### Installation

```bash
# Clone the repository
git clone https://github.com/MelihMertKorkmaz/Daily-Tech-News.git
cd Daily-Tech-News

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install django feedparser requests beautifulsoup4 google-generativeai python-dotenv celery django-celery-beat redis

# Set up environment variables
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run migrations
python3 manage.py migrate

# Add RSS sources via Django admin
python3 manage.py createsuperuser
python3 manage.py runserver
# → Visit http://localhost:8000/admin to add RSS feed sources
```

### Running the Pipeline

```bash
# Full pipeline — fetch articles & generate AI summaries
python3 commands/fetch_and_summarize.py

# Or run steps individually
python3 commands/fetch.py          # Fetch articles only
python3 commands/summarize.py      # Generate summaries only
```

### Viewing the Digest

```bash
python3 manage.py runserver
# → Visit http://localhost:8000
```

---

## 🔄 How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  RSS Feeds   │────▶│  Fetch & Scrape   │────▶│  Gemini AI       │────▶│  Django Web  │
│  (Tech &     │     │  (feedparser +    │     │  Summarization   │     │  Interface   │
│   Politics)  │     │   BeautifulSoup)  │     │  (per-article)   │     │  (slideshow) │
└──────────────┘     └──────────────────┘     └──────────────────┘     └──────────────┘
                         │                         │
                         ▼                         ▼
                   ┌─────────────┐          ┌─────────────┐
                   │  Duplicate  │          │  Duplicate   │
                   │  Filtering  │          │  Filtering   │
                   │  (ingestion)│          │  (AI output) │
                   └─────────────┘          └─────────────┘
```

1. **Fetch** — Collects RSS entries for the target date, scrapes full article text and OG images
2. **Deduplicate** — Removes cross-source duplicates using title word-overlap (60% threshold)
3. **Summarize** — Sends articles to Gemini with structured prompting to generate per-article summaries
4. **Display** — Renders summaries as navigable cards with article images and source links

---

## 📸 UI Preview

- **Homepage** — Date-based archive list for browsing past digests
- **Daily Summary** — Slideshow view with article cards, images, and source links
- **Dark Mode** — Persistent light/dark theme toggle with localStorage


