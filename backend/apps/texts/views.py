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
    filterset_fields = ['language', 'difficulty', 'kind', 'theme']
    
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
    
    @action(detail=False, methods=['get'])
    def practice_items(self, request):
        """
        연습용 아이템 조회 API (v4.0 스펙)
        
        Query Parameters:
        - mode: word | short (기본: word)
        - language: ko | en (기본: ko)
        - difficulty: 1 | 2 | 3 (기본: 1)
        - count: 반환할 아이템 수 (기본: 10, 최대: 50)
        
        Returns:
        - items: 텍스트 콘텐츠 목록
        - pack_code: 사용된 팩 코드
        - total_available: 해당 팩의 전체 아이템 수
        """
        mode = request.query_params.get('mode', 'word')
        language = request.query_params.get('language', 'ko')
        difficulty = request.query_params.get('difficulty', '1')
        count = min(int(request.query_params.get('count', '10')), 50)
        
        # mode 매핑
        kind = mode  # word -> word, short -> short
        theme = 'proverb' if mode == 'short' else 'daily'
        
        # 팩 조회
        pack = TextPack.objects.filter(
            language=language,
            kind=kind,
            theme=theme,
            difficulty=int(difficulty),
            is_active=True
        ).first()
        
        if not pack:
            return Response({
                'items': [],
                'pack_code': None,
                'total_available': 0,
                'message': f'해당 조건의 팩이 없습니다. (mode={mode}, lang={language}, diff={difficulty})'
            })
        
        # 아이템 조회 (랜덤 정렬)
        items = pack.items.filter(is_active=True).order_by('?')[:count]
        
        return Response({
            'items': [item.content for item in items],
            'pack_code': pack.code,
            'total_available': pack.items.filter(is_active=True).count()
        })
