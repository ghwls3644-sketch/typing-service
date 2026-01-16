from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyChallengeViewSet, UserChallengeViewSet

router = DefaultRouter()
router.register('daily', DailyChallengeViewSet, basename='daily-challenges')
router.register('my', UserChallengeViewSet, basename='user-challenges')

urlpatterns = [
    path('', include(router.urls)),
]
