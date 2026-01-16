from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BadgeViewSet, UserBadgeViewSet, UserLevelViewSet

router = DefaultRouter()
router.register('badges', BadgeViewSet, basename='badges')
router.register('my-badges', UserBadgeViewSet, basename='user-badges')
router.register('level', UserLevelViewSet, basename='user-level')

urlpatterns = [
    path('', include(router.urls)),
]
