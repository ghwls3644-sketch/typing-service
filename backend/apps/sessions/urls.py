from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TypingSessionViewSet

router = DefaultRouter()
router.register('', TypingSessionViewSet, basename='sessions')

urlpatterns = [
    path('', include(router.urls)),
]
