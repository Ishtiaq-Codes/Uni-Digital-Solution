from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('create/', views.course_create, name='create'),
    path('<uuid:pk>/', views.course_detail, name='detail'),
    path('<uuid:pk>/edit/', views.course_edit, name='edit'),
    path('<uuid:pk>/upload-material/', views.upload_material, name='upload_material'),
    path('<uuid:pk>/create-assignment/', views.create_assignment, name='create_assignment'),
    path('<uuid:pk>/enroll/', views.enroll_course, name='enroll'),
    path('material/<uuid:pk>/download/', views.download_material, name='download_material'),
]
