from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Max
from datetime import date, timedelta
from .models import UserDaily
from .serializers import UserDailySerializer, UserDailyListSerializer, StatsOverviewSerializer


class UserDailyViewSet(viewsets.ReadOnlyModelViewSet):
    """일일 통계 API"""
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
        
        # 최근 30일 통계
        thirty_days_ago = date.today() - timedelta(days=30)
        recent = queryset.filter(date__gte=thirty_days_ago)
        
        stats = recent.aggregate(
            total_sessions=Sum('total_sessions'),
            total_duration_ms=Sum('total_duration_ms'),
            avg_wpm=Avg('avg_wpm'),
            avg_accuracy=Avg('avg_accuracy'),
            best_wpm=Max('best_wpm'),
        )
        
        # 스트릭 정보
        streak_info = {'current_streak': 0, 'longest_streak': 0}
        if hasattr(request.user, 'streak') and request.user.streak:
            streak_info = {
                'current_streak': request.user.streak.current_streak,
                'longest_streak': request.user.streak.longest_streak,
            }
        
        data = {
            'total_sessions': stats.get('total_sessions') or 0,
            'total_duration_ms': stats.get('total_duration_ms') or 0,
            'avg_wpm': stats.get('avg_wpm') or 0,
            'avg_accuracy': stats.get('avg_accuracy') or 0,
            'best_wpm': stats.get('best_wpm'),
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
