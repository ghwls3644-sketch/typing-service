from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Max
from django.utils import timezone
from datetime import timedelta
from .models import UserDaily, ClientDaily
from .serializers import (
    UserDailySerializer, UserDailyListSerializer,
    ClientDailySerializer, StatsOverviewSerializer
)


class UserDailyViewSet(viewsets.ReadOnlyModelViewSet):
    """일일 통계 API (로그인 사용자)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserDaily.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserDailyListSerializer
        return UserDailySerializer
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """통계 요약 조회"""
        queryset = self.get_queryset()
        
        thirty_days_ago = timezone.localdate() - timedelta(days=30)
        recent = queryset.filter(date__gte=thirty_days_ago)
        
        stats = recent.aggregate(
            total_sessions=Sum('total_sessions'),
            total_duration_ms=Sum('total_duration_ms'),
            avg_wpm=Avg('avg_wpm'),
            avg_accuracy=Avg('avg_accuracy'),
            best_wpm=Max('best_wpm'),
        )
        
        streak_info = {'current_streak': 0, 'longest_streak': 0}
        if hasattr(request.user, 'streak') and request.user.streak:
            streak_info = {
                'current_streak': request.user.streak.current_streak,
                'longest_streak': request.user.streak.longest_streak,
            }
        
        # 오늘 통계
        today_stats = queryset.filter(date=timezone.localdate()).aggregate(
            today_sessions=Sum('total_sessions'),
            today_duration_ms=Sum('total_duration_ms'),
            today_avg_wpm=Avg('avg_wpm'),
            today_avg_accuracy=Avg('avg_accuracy'),
        )
        
        data = {
            'total_sessions': stats.get('total_sessions') or 0,
            'total_duration_ms': stats.get('total_duration_ms') or 0,
            'avg_wpm': stats.get('avg_wpm') or 0,
            'avg_accuracy': stats.get('avg_accuracy') or 0,
            'best_wpm': stats.get('best_wpm'),
            'today_sessions': today_stats.get('today_sessions') or 0,
            'today_duration_ms': today_stats.get('today_duration_ms') or 0,
            'today_avg_wpm': today_stats.get('today_avg_wpm') or 0,
            'today_avg_accuracy': today_stats.get('today_avg_accuracy') or 0,
            **streak_info,
        }
        
        serializer = StatsOverviewSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """캘린더용 데이터 조회 (date range)"""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        
        queryset = self.get_queryset()
        
        if start:
            queryset = queryset.filter(date__gte=start)
        if end:
            queryset = queryset.filter(date__lte=end)
        
        serializer = UserDailyListSerializer(queryset, many=True)
        return Response(serializer.data)


class ClientDailyViewSet(viewsets.ViewSet):
    """익명 일일 통계 API (guest_session_id 기반)"""
    permission_classes = [permissions.AllowAny]
    
    def _get_guest_id(self, request):
        return request.query_params.get('guest_session_id', '')
    
    def list(self, request):
        """일간 통계 목록 (최근 N일)"""
        guest_id = self._get_guest_id(request)
        if not guest_id:
            return Response({'error': 'guest_session_id 필수'}, status=400)
        
        try:
            days = int(request.query_params.get('days', 30))
        except (ValueError, TypeError):
            return Response({'error': 'days는 정수여야 합니다.'}, status=400)
        lang = request.query_params.get('lang')
        
        start_date = timezone.localdate() - timedelta(days=days)
        queryset = ClientDaily.objects.filter(
            guest_session_id=guest_id,
            date__gte=start_date
        )
        if lang:
            queryset = queryset.filter(language=lang)
        
        serializer = ClientDailySerializer(queryset.order_by('-date'), many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """대시보드용 통계 요약 (스트릭 포함)"""
        guest_id = self._get_guest_id(request)
        if not guest_id:
            return Response({'error': 'guest_session_id 필수'}, status=400)
        
        thirty_days_ago = timezone.localdate() - timedelta(days=30)
        recent = ClientDaily.objects.filter(
            guest_session_id=guest_id,
            date__gte=thirty_days_ago
        )
        
        stats = recent.aggregate(
            total_sessions=Sum('total_sessions'),
            total_duration_ms=Sum('total_duration_ms'),
            avg_wpm=Avg('avg_wpm'),
            avg_accuracy=Avg('avg_accuracy'),
            best_wpm=Max('best_wpm'),
        )
        
        # 스트릭
        from apps.goals.models import ClientStreak
        streak_info = {'current_streak': 0, 'longest_streak': 0}
        try:
            streak = ClientStreak.objects.get(guest_session_id=guest_id)
            streak_info = {
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
            }
        except ClientStreak.DoesNotExist:
            pass
        
        # 오늘 통계
        today_data = ClientDaily.objects.filter(
            guest_session_id=guest_id,
            date=timezone.localdate()
        ).aggregate(
            today_sessions=Sum('total_sessions'),
            today_duration_ms=Sum('total_duration_ms'),
            today_avg_wpm=Avg('avg_wpm'),
            today_avg_accuracy=Avg('avg_accuracy'),
        )
        
        data = {
            'total_sessions': stats.get('total_sessions') or 0,
            'total_duration_ms': stats.get('total_duration_ms') or 0,
            'avg_wpm': stats.get('avg_wpm') or 0,
            'avg_accuracy': stats.get('avg_accuracy') or 0,
            'best_wpm': stats.get('best_wpm'),
            'today_sessions': today_data.get('today_sessions') or 0,
            'today_duration_ms': today_data.get('today_duration_ms') or 0,
            'today_avg_wpm': today_data.get('today_avg_wpm') or 0,
            'today_avg_accuracy': today_data.get('today_avg_accuracy') or 0,
            **streak_info,
        }
        
        serializer = StatsOverviewSerializer(data)
        return Response(serializer.data)
