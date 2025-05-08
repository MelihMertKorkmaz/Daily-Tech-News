import datetime
from .models import Article, DailySummary
from .gemini import model
import logging

logger = logging.getLogger(__name__)

def generate_summary(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()

    articles = Article.objects.filter(published__date=specified_date)
    if not articles:
        logger.info(f"No articles found for {specified_date}.")
        return "No articles found for today."

    article_blocks = []
    for idx, article in enumerate(articles, 1):
        block = f"{idx}. {article.title}\n{article.full_text.strip()}\n[Read more]({article.link})"
        article_blocks.append(block)

    full_prompt = (
        "You are an expert tech news editor. From the news articles I provide, summarize each piece into 8-10 clear, concise sentences that retain all critical details. "+
        "Use this format: first article '\n\n' second article '\n\n' third article... "+
        " Do not add any commentary, greetings, or explanations. Just return the formatted summaries. NO ORDER INDEX, OR ANY SYMBOLS IN THE BEGINNING. Start with the article"
        + "\n\n" + "\n\n".join(article_blocks)
    )

    try:
        response = model.generate_content(full_prompt)
        summary_text = response.candidates[0].content.parts[0].text

        daily_summary, _ = DailySummary.objects.get_or_create(date=specified_date)
        daily_summary.summary = summary_text
        daily_summary.save()

        logger.info(f"Summary generated and saved for {specified_date}.")
        return summary_text
    except Exception as e:
        logger.error(f"Failed to generate summary for {specified_date}: {e}")
        return f"Failed to generate summary: {e}"
