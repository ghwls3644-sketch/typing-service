from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import TextPack, TextItem
from .serializers import (
    TextPackSerializer, TextPackListSerializer, TextPackDetailSerializer,
    TextItemSerializer, TextItemListSerializer
)
import random


class TextPackViewSet(viewsets.ReadOnlyModelViewSet):
    """문장팩 조회 API"""
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['language', 'difficulty']
    
    def get_queryset(self):
        return TextPack.objects.filter(is_active=True).prefetch_related('items')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TextPackListSerializer
        if self.action == 'retrieve':
            return TextPackDetailSerializer
        return TextPackSerializer
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """랜덤 문장팩 조회"""
        language = request.query_params.get('language')
        difficulty = request.query_params.get('difficulty')
        
        queryset = self.get_queryset()
        if language:
            queryset = queryset.filter(language=language)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        if queryset.exists():
            pack = random.choice(list(queryset))
            serializer = TextPackDetailSerializer(pack)
            return Response(serializer.data)
        
        return Response({'detail': '해당 조건의 문장팩이 없습니다.'}, status=404)


class TextItemViewSet(viewsets.ReadOnlyModelViewSet):
    """문장 조회 API"""
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pack', 'is_active']
    
    def get_queryset(self):
        return TextItem.objects.filter(is_active=True).select_related('pack')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TextItemListSerializer
        return TextItemSerializer
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """랜덤 문장 조회"""
        pack_id = request.query_params.get('pack')
        language = request.query_params.get('language')
        
        queryset = self.get_queryset()
        if pack_id:
            queryset = queryset.filter(pack_id=pack_id)
        if language:
            queryset = queryset.filter(pack__language=language)
        
        if queryset.exists():
            item = random.choice(list(queryset))
            serializer = TextItemSerializer(item)
            return Response(serializer.data)
        
        return Response({'detail': '해당 조건의 문장이 없습니다.'}, status=404)
