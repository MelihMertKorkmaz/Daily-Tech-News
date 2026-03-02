import datetime
import time
import re
from .models import Article, DailySummary, ArticlePolitics, DailySummaryPolitics
from .gemini import model
import logging

logger = logging.getLogger(__name__)


def deduplicate_articles(articles):
    """Remove cross-source duplicates by checking for very similar titles."""
    seen_titles = []
    unique = []
    for article in articles:
        title_lower = article.title.lower().strip()
        # Check if a very similar title already exists
        is_dupe = False
        for seen in seen_titles:
            # Simple check: if titles share 60%+ of their words, consider it a duplicate
            words_a = set(title_lower.split())
            words_b = set(seen.split())
            if not words_a or not words_b:
                continue
            overlap = len(words_a & words_b) / min(len(words_a), len(words_b))
            if overlap >= 0.6:
                is_dupe = True
                break
        if not is_dupe:
            seen_titles.append(title_lower)
            unique.append(article)
    return unique


def deduplicate_summary(summary_text):
    """Remove duplicate TITLE blocks from Gemini output (keeps first occurrence)."""
    blocks = re.split(r'\n{2,}(?=TITLE:)', summary_text.strip())
    seen_titles = set()
    unique_blocks = []
    for block in blocks:
        # Extract title from block
        title = ''
        for line in block.strip().split('\n'):
            if line.startswith('TITLE:'):
                title = line[6:].strip().lower()
                break
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block.strip())
        elif not title:
            # Keep blocks without a TITLE (edge case)
            unique_blocks.append(block.strip())
    return '\n\n'.join(unique_blocks)

def generate_summary(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()

    articles = Article.objects.filter(published__date=specified_date)
    if not articles:
        logger.warning(f"[TECH SUMMARY] ⚠️  No articles found for {specified_date} — nothing to summarize.")
        return "No articles found for today."

    logger.info(f"[TECH SUMMARY] Found {articles.count()} articles for {specified_date}")

    # Deduplicate cross-source articles
    unique_articles = deduplicate_articles(list(articles))
    logger.info(f"[TECH SUMMARY] After dedup: {len(unique_articles)} unique articles")

    article_blocks = []
    for idx, article in enumerate(unique_articles, 1):
        block = f"TITLE: {article.title}\nLINK: {article.link}\n{article.full_text.strip()}"
        article_blocks.append(block)

    full_prompt = (
        "You are an expert tech news editor. From the news articles I provide, summarize each piece into 8-10 clear, concise sentences that retain all critical details. "
        "For EACH article, you MUST output EXACTLY this format:\n"
        "TITLE: <the exact title as given>\n"
        "LINK: <the exact link as given>\n"
        "<your summary>\n\n"
        "Separate each article with a blank line. Do not reorder the articles. "
        "Do not add any commentary, greetings, or explanations. Do not add numbering or symbols before the TITLE line. "
        "Output EXACTLY one summary per article. Do NOT repeat any article."
        + "\n\n" + "\n\n".join(article_blocks)
    )

    logger.info(f"[TECH SUMMARY] Sending prompt to Gemini ({len(full_prompt)} chars)...")

    try:
        response = model.generate_content(full_prompt)
        summary_text = response.candidates[0].content.parts[0].text

        # Deduplicate Gemini output as safety net
        summary_text = deduplicate_summary(summary_text)

        daily_summary, _ = DailySummary.objects.get_or_create(date=specified_date)
        daily_summary.summary = summary_text
        daily_summary.save()

        logger.info(f"[TECH SUMMARY] ✅ Summary generated and saved for {specified_date} ({len(summary_text)} chars)")
        return summary_text
    except Exception as e:
        logger.error(f"[TECH SUMMARY] ❌ Failed to generate summary for {specified_date}: {e}")
        return f"Failed to generate summary: {e}"


    #--------------POLITICS---------------


def generate_summary_politics(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()

    articles = ArticlePolitics.objects.filter(published__date=specified_date)
    if not articles:
        logger.warning(f"[POLITICS SUMMARY] ⚠️  No articles found for {specified_date} — nothing to summarize.")
        return "No articles found for today."

    logger.info(f"[POLITICS SUMMARY] Found {articles.count()} articles for {specified_date}")

    # Deduplicate cross-source articles
    unique_articles = deduplicate_articles(list(articles))
    logger.info(f"[POLITICS SUMMARY] After dedup: {len(unique_articles)} unique articles")

    article_blocks = []
    for idx, article in enumerate(unique_articles, 1):
        block = f"TITLE: {article.title}\nLINK: {article.link}\n{article.full_text.strip()}"
        article_blocks.append(block)

    full_prompt = (
        "You are an expert world politics news editor. From the news articles I provide, summarize each piece into 8-10 clear, concise sentences that retain all critical details. "
        "For EACH article, you MUST output EXACTLY this format:\n"
        "TITLE: <the exact title as given>\n"
        "LINK: <the exact link as given>\n"
        "<your summary>\n\n"
        "Separate each article with a blank line. Do not reorder the articles. "
        "Do not add any commentary, greetings, or explanations. Do not add numbering or symbols before the TITLE line. "
        "Output EXACTLY one summary per article. Do NOT repeat any article."
        + "\n\n" + "\n\n".join(article_blocks)
    )

    logger.info(f"[POLITICS SUMMARY] Sending prompt to Gemini ({len(full_prompt)} chars)...")

    try:
        response = model.generate_content(full_prompt)
        summary_text = response.candidates[0].content.parts[0].text

        # Deduplicate Gemini output as safety net
        summary_text = deduplicate_summary(summary_text)

        daily_summary, _ = DailySummaryPolitics.objects.get_or_create(date=specified_date)
        daily_summary.summary = summary_text
        daily_summary.save()

        logger.info(f"[POLITICS SUMMARY] ✅ Summary generated and saved for {specified_date} ({len(summary_text)} chars)")
        return summary_text
    except Exception as e:
        logger.error(f"[POLITICS SUMMARY] ❌ Failed to generate summary for {specified_date}: {e}")
        return f"Failed to generate summary: {e}"

