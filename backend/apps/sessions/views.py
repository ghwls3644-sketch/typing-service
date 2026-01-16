from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Sum, Count
from django.utils import timezone
from datetime import date
from .models import TypingSession
from .serializers import (
    TypingSessionSerializer, 
    TypingSessionCreateSerializer,
    TypingSessionListSerializer,
    UserStatsSerializer
)


class TypingSessionViewSet(viewsets.ModelViewSet):
    """타자 세션 API"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = TypingSession.objects.all()
        
        # 로그인한 사용자는 자신의 기록만
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        else:
            # 비로그인 사용자는 guest_session_id로 필터링
            session_id = self.request.query_params.get('guest_session_id')
            if session_id:
                queryset = queryset.filter(guest_session_id=session_id)
            else:
                queryset = queryset.none()
        
        # 필터
        language = self.request.query_params.get('language')
        mode = self.request.query_params.get('mode')
        
        if language:
            queryset = queryset.filter(language=language)
        if mode:
            queryset = queryset.filter(mode=mode)
        
        return queryset.order_by('-started_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TypingSessionCreateSerializer
        if self.action == 'list':
            return TypingSessionListSerializer
        return TypingSessionSerializer
    
    def perform_create(self, serializer):
        session = serializer.save()
        
        # 스트릭 업데이트 (로그인 사용자만)
        if self.request.user.is_authenticated:
            self._update_daily_stats(session)
            self._update_streak(session)
    
    def _update_daily_stats(self, session):
        """일일 통계 업데이트 (write-through)"""
        from apps.stats.models import UserDaily
        
        today = timezone.localdate()
        user_daily, created = UserDaily.objects.get_or_create(
            user=session.user,
            date=today,
            language=session.language,
            defaults={
                'total_sessions': 0,
                'total_duration_ms': 0,
                'avg_wpm': 0,
                'avg_accuracy': 0,
            }
        )
        
        # 업데이트
        user_daily.total_sessions += 1
        user_daily.total_duration_ms += session.duration_ms
        user_daily.total_chars += session.input_length
        user_daily.total_errors += session.error_count
        
        # 평균 재계산 (간단 버전)
        sessions_today = TypingSession.objects.filter(
            user=session.user, 
            language=session.language,
            started_at__date=today
        )
        agg = sessions_today.aggregate(
            avg_wpm=Avg('wpm'),
            avg_accuracy=Avg('accuracy'),
            best_wpm=Max('wpm'),
            best_accuracy=Max('accuracy'),
        )
        user_daily.avg_wpm = agg.get('avg_wpm') or 0
        user_daily.avg_accuracy = agg.get('avg_accuracy') or 0
        user_daily.best_wpm = agg.get('best_wpm')
        user_daily.best_accuracy = agg.get('best_accuracy')
        user_daily.save()
    
    def _update_streak(self, session):
        """스트릭 업데이트"""
        from apps.goals.models import UserStreak
        
        streak, created = UserStreak.objects.get_or_create(user=session.user)
        streak.update_streak(timezone.localdate())
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """사용자 통계 조회"""
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'total_sessions': 0,
                'avg_wpm': 0,
                'avg_accuracy': 0,
                'best_wpm': None,
                'total_time_ms': 0,
                'korean_sessions': 0,
                'english_sessions': 0,
            })
        
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            avg_wpm=Avg('wpm'),
            avg_accuracy=Avg('accuracy'),
            best_wpm=Max('wpm'),
            total_time_ms=Sum('duration_ms'),
        )
        
        stats['korean_sessions'] = queryset.filter(language='ko').count()
        stats['english_sessions'] = queryset.filter(language='en').count()
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """최근 기록 조회 (최대 10개)"""
        queryset = self.get_queryset()[:10]
        serializer = TypingSessionListSerializer(queryset, many=True)
        return Response(serializer.data)
