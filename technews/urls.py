from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.global_home_view, name='global_home'),
    path('tech/', include('news.urls')),
    path('politics/', include('news.urls_politics')),
]
