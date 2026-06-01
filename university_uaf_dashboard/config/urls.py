"""
Root URL Configuration for UAF Smart Dashboard System.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
    path('fees/', include('apps.fees.urls')),
    path('forms/', include('apps.form_manager.urls')),
    path('qec/', include('apps.qec.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('university/', include('apps.university.urls')),
    path('reports/', include('apps.reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = 'UAF Smart Dashboard Administration'
admin.site.site_title = 'UAF Admin'
admin.site.index_title = 'Administration Panel'
