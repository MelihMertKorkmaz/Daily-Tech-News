from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('<str:date>/', views.daily_summary_by_date_view, name='daily_summary_by_date'),

]