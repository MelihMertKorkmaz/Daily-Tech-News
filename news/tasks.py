from celery import shared_task
from .fetch_articles import fetch_and_parse_feeds
import datetime

@shared_task
def fetch_articles_task():
    today = datetime.date.today()
    fetch_and_parse_feeds(today)
