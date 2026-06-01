from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.voucher_list, name='list'),
    path('create/', views.voucher_create, name='create'),
    path('<uuid:pk>/', views.voucher_detail, name='detail'),
    path('<uuid:pk>/upload-receipt/', views.upload_receipt, name='upload_receipt'),
    path('payment/<uuid:pk>/verify/', views.verify_payment, name='verify_payment'),
]
