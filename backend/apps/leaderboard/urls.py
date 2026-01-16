from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SnapshotViewSet, EntryViewSet

router = DefaultRouter()
router.register('snapshots', SnapshotViewSet, basename='leaderboard-snapshots')
router.register('entries', EntryViewSet, basename='leaderboard-entries')

urlpatterns = [
    path('', include(router.urls)),
]
