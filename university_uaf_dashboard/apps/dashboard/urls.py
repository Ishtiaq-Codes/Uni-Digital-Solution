"""
URL patterns for dashboard app - includes landing page and dashboard routes.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_home, name='home'),
    path('search/', views.global_search, name='search'),
]
