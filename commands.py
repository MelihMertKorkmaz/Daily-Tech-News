from news.fetch_articles import fetch_and_parse_feeds , fetch_and_parse_feeds_politics
from news.summarizer import generate_summary, generate_summary_politics
# to achieve easy terminal usage when running these commands manually.
def fetch():
    fetch_and_parse_feeds()
    print('fetch_and_parse_feeds')
    fetch_and_parse_feeds_politics()
    print('fetch_and_parse_feeds_politics')

def generate():
    generate_summary()
    print('generate_summary')
    generate_summary_politics()
    print('generate_summary_politics')