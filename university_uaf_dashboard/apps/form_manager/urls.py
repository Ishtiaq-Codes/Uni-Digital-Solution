from django.urls import path
from . import views

app_name = 'form_manager'

urlpatterns = [
    path('', views.form_template_list, name='list'),
    path('submit/<uuid:pk>/', views.form_submit, name='submit'),
    path('my-submissions/', views.my_submissions, name='submissions'),
    path('submission/<uuid:pk>/', views.submission_detail, name='submission_detail'),
    path('submission/<uuid:pk>/review/', views.review_submission, name='review'),
    path('all-submissions/', views.all_submissions, name='all_submissions'),
    path('create-template/', views.create_template, name='create_template'),
]
