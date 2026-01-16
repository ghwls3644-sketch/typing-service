from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextPackViewSet, TextItemViewSet

router = DefaultRouter()
router.register('packs', TextPackViewSet, basename='text-packs')
router.register('items', TextItemViewSet, basename='text-items')

urlpatterns = [
    path('', include(router.urls)),
]
