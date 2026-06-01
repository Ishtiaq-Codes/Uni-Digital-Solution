from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics'),
    path('export/students/', views.export_students_csv, name='export_students'),
    path('export/fees/', views.export_fees_csv, name='export_fees'),
    path('export/qec/', views.export_qec_csv, name='export_qec'),
]
