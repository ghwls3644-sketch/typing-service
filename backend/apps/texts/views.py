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
        연습용 아이템 조회 API (v4.0 스펙 - Length Based Difficulty)
        
        Query Parameters:
        - mode: word | short (기본: word)
        - language: ko | en (기본: ko)
        - difficulty: 1 | 2 | 3 (기본: 1)
        - count: 반환할 아이템 수 (기본: 10, 최대: 50)
        """
        mode = request.query_params.get('mode', 'word')
        language = request.query_params.get('language', 'ko')
        difficulty = int(request.query_params.get('difficulty', '1'))
        count = min(int(request.query_params.get('count', '10')), 50)
        
        # 1. 기본 쿼리셋 (언어, 모드, 활성화)
        kind = mode
        theme = 'proverb' if mode == 'short' else 'daily'
        
        base_query = TextItem.objects.filter(
            pack__language=language,
            pack__kind=kind,
            pack__theme=theme,
            is_active=True
        )
        
        # 2. 난이도별 글자 수 범위 정의
        length_ranges = {
            'ko': {
                'word': {1: (0, 3), 2: (4, 6), 3: (7, 12)},
                'short': {1: (0, 12), 2: (13, 18), 3: (19, 999)}
            },
            'en': {
                'word': {1: (0, 4), 2: (5, 7), 3: (8, 999)},
                'short': {1: (0, 30), 2: (31, 50), 3: (51, 999)}
            }
        }
        
        min_len, max_len = length_ranges.get(language, {}).get(mode, {}).get(difficulty, (0, 999))

        # 2. 모드별 필터링 (단어/짧은글)
        if mode:
            base_query = base_query.filter(pack__kind=mode)
            # 단어 모드: 공백이 포함된 아이템 제외 (문장 혼입 방지)
            if mode == 'word':
                base_query = base_query.exclude(content__contains=' ')
        
        # 3. 길이 기반 필터링
        filtered_items = base_query.filter(length__gte=min_len, length__lte=max_len)
        
        # 4. Fallback: 조건에 맞는 아이템이 너무 적으면(< 5) 전체 범위에서 랜덤
        # (요청한 count보다 적더라도, 최소 5개(한 세트 분량) 이상이면 해당 난이도 아이템만 반환)
        available_count = filtered_items.count()
        
        if available_count < 5:
            final_items = base_query.order_by('?')[:count]
            pack_code = "fallback-mixed"
        else:
            # 요청 수보다 적으면 있는 만큼만 반환
            limit = min(count, available_count)
            final_items = filtered_items.order_by('?')[:limit]
            pack_code = f"{language}-{mode}-diff{difficulty}"

        return Response({
            'items': [item.content for item in final_items],
            'pack_code': pack_code,
            'total_available': available_count
        })
