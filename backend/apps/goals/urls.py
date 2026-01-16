from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserGoalViewSet, UserStreakViewSet

router = DefaultRouter()
router.register('goals', UserGoalViewSet, basename='goals')
router.register('streaks', UserStreakViewSet, basename='streaks')

urlpatterns = [
    path('', include(router.urls)),
]
