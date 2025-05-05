import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
from .models import RSSSource, Article
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="fetch_articles.log",
        filemode="a",
    )

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_and_parse_feeds(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()


    sources = RSSSource.objects.all()
    articles = []

    for source in sources:
        logger.info(f"Fetching feed from {source.name} ({source.url})")
        feed = feedparser.parse(source.url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            if not is_date(entry, specified_date):
                logger.info(f"Skipping article '{title}' as it is not from specified date.")
                continue

            if Article.objects.filter(link=link).exists():
                logger.info(f"Skipping duplicate article '{title}'.")
                continue

            published = None
            if hasattr(entry, "published_parsed"):
                published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

            full_text = scrape_full_text(link)

            try:
                article = Article.objects.create(
                    title=title,
                    link=link,
                    published=published,
                    full_text=full_text,
                )
                articles.append(article)
                logger.info(f"Article '{title}' successfully saved to the database.")
            except Exception as e:
                logger.error(f"Failed to save article '{title}': {e}")

    return articles


def scrape_full_text(url):
    try:
        logger.info(f"Scraping full text from {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""


def is_date(entry, specified_date):
    try:
        if hasattr(entry, "published_parsed"):
            published_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            return published_dt.date() == specified_date
        return False
    except Exception as e:
        logger.error(f"Error checking if article is from specified date: {e}")
        return False
