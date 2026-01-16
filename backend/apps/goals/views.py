from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import date
from .models import UserGoal, UserStreak
from .serializers import UserGoalSerializer, UserStreakSerializer, GoalProgressSerializer


class UserGoalViewSet(viewsets.ModelViewSet):
    """사용자 목표 API"""
    serializer_class = UserGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserGoal.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """오늘의 목표 진행률 조회"""
        from apps.stats.models import UserDaily
        
        goals = self.get_queryset()
        today = date.today()
        
        # 오늘 통계 가져오기
        today_stats = UserDaily.objects.filter(user=request.user, date=today).first()
        
        results = []
        for goal in goals:
            # 언어 필터링
            if goal.language == 'all':
                daily = UserDaily.objects.filter(user=request.user, date=today)
            else:
                daily = UserDaily.objects.filter(user=request.user, date=today, language=goal.language)
            
            # 현재 값 계산
            if goal.goal_type == 'time':
                current = sum(d.total_duration_ms for d in daily) / 60000  # 분 단위
            elif goal.goal_type == 'sessions':
                current = sum(d.total_sessions for d in daily)
            elif goal.goal_type == 'chars':
                current = sum(d.total_chars for d in daily)
            else:
                current = 0
            
            progress_percent = min((current / goal.target_value * 100) if goal.target_value else 0, 100)
            
            results.append({
                'goal': UserGoalSerializer(goal).data,
                'current_value': int(current),
                'target_value': goal.target_value,
                'progress_percent': round(progress_percent, 2),
                'is_achieved': current >= goal.target_value,
            })
        
        return Response(results)


class UserStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """사용자 스트릭 API"""
    serializer_class = UserStreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserStreak.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """내 스트릭 조회"""
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(streak)
        return Response(serializer.data)
