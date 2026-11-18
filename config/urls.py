from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manage/', include('adminpanel.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('jobs/', include('jobs.urls')),
    path('applications/', include('applications.urls')),
    path('notifications/', include('notifications.urls')),
]

# Public files only: profile photos and company logos. Resumes and documents are private.
urlpatterns += [
    re_path(
        r'^media/(?P<path>(?:profile_photos|company_logos)/.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]