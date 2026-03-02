"""
Fetch articles command.
Fetches and parses RSS feeds for both tech and politics categories.

Usage:
    python manage.py shell -c "from commands.fetch import run; run()"
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technews.settings')
django.setup()

from news.fetch_articles import fetch_and_parse_feeds, fetch_and_parse_feeds_politics


def run():
    print("Fetching tech articles...")
    fetch_and_parse_feeds()
    print("✅ Tech articles fetched.\n")

    print("Fetching politics articles...")
    fetch_and_parse_feeds_politics()
    print("✅ Politics articles fetched.")


if __name__ == "__main__":
    run()
