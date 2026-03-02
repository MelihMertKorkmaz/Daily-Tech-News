from django.shortcuts import render, get_object_or_404
from datetime import datetime
from .models import DailySummary, Article, ArticlePolitics, DailySummaryPolitics
import re


def home_view(request):
    dates = DailySummary.objects.values_list('date',
    flat=True).distinct().order_by('-date')
    formatted_dates = [
        {
            'display': date.strftime('%d %B %Y'),
            'url': date.strftime('%d-%m-%Y')
        }
        for date in dates
    ]

    return render(request, 'news/home.html',
    {'dates': formatted_dates})


def parse_summary_blocks(summary_text, articles_qs):
    """Parse summary text into structured blocks with title, link, summary, and image."""
    # Build a lookup of image_url by article link
    image_lookup = {a.link: a.image_url for a in articles_qs}

    # Split on double newlines that precede a TITLE: line
    raw_blocks = re.split(r'\n{2,}(?=TITLE:)', summary_text.strip())
    article_data = []

    for idx, block in enumerate(raw_blocks, 1):
        lines = block.strip().split('\n')
        title = ''
        link = ''
        summary_lines = []

        for line in lines:
            if line.startswith('TITLE:'):
                title = line[len('TITLE:'):].strip()
            elif line.startswith('LINK:'):
                link = line[len('LINK:'):].strip()
            else:
                summary_lines.append(line)

        summary = ' '.join(summary_lines).strip()
        image = image_lookup.get(link, None)

        if title and summary:
            article_data.append((idx, title, summary, link, image))

    return article_data


def daily_summary_by_date_view(request, date):
    try:
        parsed_date = datetime.strptime(date, '%d-%m-%Y').date()
    except ValueError:
        return render(request, 'news/invalid_date.html',
        status=400)

    summary = get_object_or_404(DailySummary, date=parsed_date)
    articles = Article.objects.filter(published__date=parsed_date)
    article_data = parse_summary_blocks(summary.summary, articles)

    return render(request, 'news/daily_summary.html', {
        'summary': summary,
        'article_data': article_data,
    })


#---------------POLITICS---------------------

def home_view_politics(request):
    dates = DailySummaryPolitics.objects.values_list('date', flat=True).distinct().order_by('-date')
    formatted_dates = [
        {
            'display': date.strftime('%d %B %Y'),
            'url': date.strftime('%d-%m-%Y')
        }
        for date in dates
    ]

    return render(request, 'news/home_politics.html', {'dates': formatted_dates})


def daily_summary_by_date_view_politics(request, date):
    try:
        parsed_date = datetime.strptime(date, '%d-%m-%Y').date()
    except ValueError:
        return render(request, 'news/invalid_date.html', status=400)

    summary = get_object_or_404(DailySummaryPolitics, date=parsed_date)
    articles = ArticlePolitics.objects.filter(published__date=parsed_date)
    article_data = parse_summary_blocks(summary.summary, articles)

    return render(request, 'news/daily_summary_politics.html', {
        'summary': summary,
        'article_data': article_data,
    })
