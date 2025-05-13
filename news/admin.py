from django.contrib import admin

from .models import RSSSource, RSSSourcePolitics

admin.site.register(RSSSource)
admin.site.register(RSSSourcePolitics)

