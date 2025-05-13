from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view_politics, name='home_politics'),
    path('<str:date>/', views.daily_summary_by_date_view_politics, name='daily_summary_by_date_politics'),

]