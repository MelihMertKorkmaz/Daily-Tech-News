from django.shortcuts import render, get_object_or_404
from datetime import datetime
from .models import DailySummary, Article, ArticlePolitics, DailySummaryPolitics


def home_view(request):
    dates = DailySummary.objects.values_list('date', flat=True).distinct().order_by('-date')
    formatted_dates = [
        {
            'display': date.strftime('%d %B %Y'),
            'url': date.strftime('%d-%m-%Y')
        }
        for date in dates
    ]

    return render(request, 'news/home.html', {'dates': formatted_dates})


def daily_summary_by_date_view(request, date):
    try:
        parsed_date = datetime.strptime(date, '%d-%m-%Y').date()
    except ValueError:
        return render(request, 'news/invalid_date.html', status=400)

    summary = get_object_or_404(DailySummary, date=parsed_date)
    articles = Article.objects.filter(published__date=parsed_date)
    links= [article.link for article in articles]
    titles= [article.title for article in articles]
    splitted_articles=summary.summary.split('\n\n')
    indexes=[n+1 for n in range(len(splitted_articles))]
    images = [article.image_url for article in articles]
    article_data= zip(indexes, titles, splitted_articles, links, images)


    return render(request, 'news/daily_summary.html', {
        'summary': summary,
        'links': links,
        'titles': titles,
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
    links= [article.link for article in articles]
    titles= [article.title for article in articles]
    splitted_articles=summary.summary.split('\n\n')
    indexes=[n+1 for n in range(len(splitted_articles))]
    images = [article.image_url for article in articles]
    article_data= zip(indexes, titles, splitted_articles, links, images)


    return render(request, 'news/daily_summary_politics.html', {
        'summary': summary,
        'links': links,
        'titles': titles,
        'article_data': article_data,

    })
