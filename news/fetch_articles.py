import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
from .models import RSSSource, Article, RSSSourcePolitics, ArticlePolitics
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="fetch_articles.log",
        filemode="a",
    )
    # Keep console output at INFO level to avoid flooding terminal
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(console)

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def fetch_feed(url):
    """Fetch RSS feed using requests (with browser UA) then parse with feedparser."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except Exception as e:
        logger.error(f"Failed to fetch feed from {url}: {e}")
        return feedparser.FeedParserDict(entries=[])

def fetch_and_parse_feeds(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()

    logger.info("="*60)
    logger.info(f"[TECH FETCH] Starting — target date: {specified_date}")
    logger.info("="*60)

    sources= RSSSource.objects.all()
    if not sources:
        logger.warning("[TECH FETCH] No RSS sources configured! Add sources via admin.")
        return []

    articles = []
    total_entries = 0
    skipped_date = 0
    skipped_duplicate = 0
    saved_count = 0
    failed_count = 0

    for source in sources:
        logger.info(f"[TECH] Fetching feed: {source.name} ({source.url})")
        feed = fetch_feed(source.url)
        source_entries = len(feed.entries)
        logger.info(f"[TECH] {source.name}: {source_entries} entries found in feed")
        total_entries += source_entries

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            if not is_date(entry, specified_date):
                logger.debug(f"[TECH] Date skip: '{title}'")
                skipped_date += 1
                continue

            if Article.objects.filter(link=link).exists():
                logger.info(f"[TECH] Duplicate skip: '{title}'")
                skipped_duplicate += 1
                continue

            published = None
            if hasattr(entry, "published_parsed"):
                published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

            full_text = scrape_full_text(link)
            image_url = fetch_og_image(link)

            try:
                article = Article.objects.create(
                    title=title,
                    link=link,
                    published=published,
                    full_text=full_text,
                    image_url= image_url
                )
                articles.append(article)
                saved_count += 1
                logger.info(f"[TECH] ✅ Saved: '{title}'")
            except Exception as e:
                failed_count += 1
                logger.error(f"[TECH] ❌ Failed to save '{title}': {e}")

    logger.info("-"*60)
    logger.info(f"[TECH FETCH] Summary for {specified_date}:")
    logger.info(f"  Sources checked : {sources.count()}")
    logger.info(f"  Total entries   : {total_entries}")
    logger.info(f"  Skipped (date)  : {skipped_date}")
    logger.info(f"  Skipped (dupe)  : {skipped_duplicate}")
    logger.info(f"  Saved           : {saved_count}")
    logger.info(f"  Failed          : {failed_count}")
    logger.info("-"*60)

    if saved_count == 0 and total_entries > 0:
        logger.warning(f"[TECH FETCH] ⚠️  0 articles saved out of {total_entries} entries! Check date filter — feeds may not have articles for {specified_date}.")

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

#to fetch overgraph image (preview image) or first image appears on the link page
def fetch_og_image(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    if og_image:
        return og_image['content']
    first_img = soup.find('img')
    if first_img and first_img.get('src'):
        return first_img['src']
    return None

def is_date(entry, specified_date):
    try:
        if hasattr(entry, "published_parsed"):
            published_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            return published_dt.date() == specified_date
        return False
    except Exception as e:
        logger.error(f"Error checking if article is from specified date: {e}")
        return False

#-------------POLITICS--------------

def fetch_and_parse_feeds_politics(specified_date=None):
    if isinstance(specified_date, str):
        specified_date = datetime.datetime.strptime(specified_date, "%d-%m-%Y").date()
    elif specified_date is None:
        specified_date = datetime.date.today()

    logger.info("="*60)
    logger.info(f"[POLITICS FETCH] Starting — target date: {specified_date}")
    logger.info("="*60)

    sources= RSSSourcePolitics.objects.all()
    if not sources:
        logger.warning("[POLITICS FETCH] No RSS sources configured! Add sources via admin.")
        return []

    articles = []
    total_entries = 0
    skipped_date = 0
    skipped_duplicate = 0
    saved_count = 0
    failed_count = 0

    for source in sources:
        logger.info(f"[POLITICS] Fetching feed: {source.name} ({source.url})")
        feed = fetch_feed(source.url)
        source_entries = len(feed.entries)
        logger.info(f"[POLITICS] {source.name}: {source_entries} entries found in feed")
        total_entries += source_entries

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            if not is_date(entry, specified_date):
                logger.debug(f"[POLITICS] Date skip: '{title}'")
                skipped_date += 1
                continue

            if ArticlePolitics.objects.filter(link=link).exists():
                logger.info(f"[POLITICS] Duplicate skip: '{title}'")
                skipped_duplicate += 1
                continue

            published = None
            if hasattr(entry, "published_parsed"):
                published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

            full_text = scrape_full_text(link)
            image_url = fetch_og_image(link)

            try:
                article = ArticlePolitics.objects.create(
                    title=title,
                    link=link,
                    published=published,
                    full_text=full_text,
                    image_url= image_url
                )
                articles.append(article)
                saved_count += 1
                logger.info(f"[POLITICS] ✅ Saved: '{title}'")
            except Exception as e:
                failed_count += 1
                logger.error(f"[POLITICS] ❌ Failed to save '{title}': {e}")

    logger.info("-"*60)
    logger.info(f"[POLITICS FETCH] Summary for {specified_date}:")
    logger.info(f"  Sources checked : {sources.count()}")
    logger.info(f"  Total entries   : {total_entries}")
    logger.info(f"  Skipped (date)  : {skipped_date}")
    logger.info(f"  Skipped (dupe)  : {skipped_duplicate}")
    logger.info(f"  Saved           : {saved_count}")
    logger.info(f"  Failed          : {failed_count}")
    logger.info("-"*60)

    if saved_count == 0 and total_entries > 0:
        logger.warning(f"[POLITICS FETCH] ⚠️  0 articles saved out of {total_entries} entries! Check date filter — feeds may not have articles for {specified_date}.")

    return articles