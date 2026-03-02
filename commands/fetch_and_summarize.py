"""
Fetch articles + Generate summaries — all in one command.

Runs the full pipeline:
  1. Fetch tech articles from RSS feeds
  2. Fetch politics articles from RSS feeds
  3. Generate AI summary for tech articles
  4. Generate AI summary for politics articles

Usage:
    python commands/fetch_and_summarize.py
"""
import django
import os
import sys
import time

# Ensure the project root (where manage.py lives) is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technews.settings')
django.setup()

from news.fetch_articles import fetch_and_parse_feeds, fetch_and_parse_feeds_politics
from news.summarizer import generate_summary, generate_summary_politics


def run():
    print("=" * 50)
    print("  NEWSDIGEST — Full Pipeline")
    print("=" * 50)

    # --- FETCH ---
    print("\n[1/4] Fetching tech articles...")
    fetch_and_parse_feeds()
    print("✅ Tech articles fetched.")

    print("\n[2/4] Fetching politics articles...")
    fetch_and_parse_feeds_politics()
    print("✅ Politics articles fetched.")

    # Brief pause before hitting the Gemini API
    print("\n⏳ Waiting before generating summaries...")
    time.sleep(3)

    # --- SUMMARIZE ---
    print("\n[3/4] Generating tech summary...")
    generate_summary()
    print("✅ Tech summary generated.")

    # Delay between API calls to avoid rate limits
    time.sleep(5)

    print("\n[4/4] Generating politics summary...")
    generate_summary_politics()
    print("✅ Politics summary generated.")

    print("\n" + "=" * 50)
    print("  ✅ Pipeline complete!")
    print("=" * 50)


if __name__ == "__main__":
    run()
