"""
URL patterns for accounts app.
Registration route is kept but disabled (redirects to login with a warning).
User creation is restricted to admin-only routes.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Public auth routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),

    # Disabled public registration (redirects to login with warning)
    path('register/', views.register_view, name='register'),

    # Authenticated user routes
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    # Admin-only user management
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.create_user_view, name='create_user'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user_active'),
    path('users/<int:pk>/reset-password/', views.admin_reset_password_view, name='admin_reset_password'),
]
