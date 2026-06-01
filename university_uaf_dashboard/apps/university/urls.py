from django.urls import path
from . import views

app_name = 'university'

urlpatterns = [
    path('departments/', views.departments_page, name='departments'),
    path('departments/<uuid:pk>/', views.department_detail, name='department_detail'),
    path('announcements/', views.announcements_page, name='announcements'),
    path('announcements/<uuid:pk>/', views.announcement_detail, name='announcement_detail'),
    path('calendar/', views.academic_calendar, name='calendar'),
    path('faculty/', views.faculty_directory, name='faculty'),
    path('about/', views.about_page, name='about'),
    path('features/', views.features_page, name='features'),
    path('contact/', views.contact_page, name='contact'),
]
