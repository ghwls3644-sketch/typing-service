from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDailyViewSet

router = DefaultRouter()
router.register('daily', UserDailyViewSet, basename='stats-daily')

urlpatterns = [
    path('', include(router.urls)),
]
