from django.urls import path
from . import views

app_name = 'qec'

urlpatterns = [
    path('', views.feedback_list, name='list'),
    path('submit/', views.submit_feedback, name='submit'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
]
