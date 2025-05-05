from django.db import models

class RSSSource(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

class Article(models.Model):
    title = models.CharField(max_length=255)
    link= models.URLField()
    published= models.DateTimeField(null=True)
    full_text = models.TextField(default="No text available")
    def __repr__(self):
        return self.title

class DailySummary(models.Model):
    date = models.DateField(unique=True)
    summary = models.TextField(default="No summary available")


    def __str__(self):
        return "Daily News Reports in TECH"