from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDailyViewSet, ClientDailyViewSet

router = DefaultRouter()
router.register('daily', UserDailyViewSet, basename='stats-daily')
router.register('client', ClientDailyViewSet, basename='stats-client')

urlpatterns = [
    path('', include(router.urls)),
]
