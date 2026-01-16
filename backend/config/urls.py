"""
URL configuration for typing service project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/texts/', include('apps.texts.urls')),
    path('api/sessions/', include('apps.sessions.urls')),
    path('api/stats/', include('apps.stats.urls')),
    path('api/goals/', include('apps.goals.urls')),
    path('api/leaderboard/', include('apps.leaderboard.urls')),
    path('api/challenges/', include('apps.challenges.urls')),
    path('api/achievements/', include('apps.achievements.urls')),
]

# Debug toolbar (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
