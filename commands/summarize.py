"""
Generate summaries command.
Generates AI summaries for both tech and politics articles.

Usage:
    python manage.py shell -c "from commands.summarize import run; run()"
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technews.settings')
django.setup()

from news.summarizer import generate_summary, generate_summary_politics


def run():
    print("Generating tech summary...")
    generate_summary()
    print("✅ Tech summary generated.\n")

    print("Generating politics summary...")
    generate_summary_politics()
    print("✅ Politics summary generated.")


if __name__ == "__main__":
    run()
