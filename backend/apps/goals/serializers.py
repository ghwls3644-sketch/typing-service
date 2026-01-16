from rest_framework import serializers
from .models import UserGoal, UserStreak


class UserGoalSerializer(serializers.ModelSerializer):
    """사용자 목표 직렬화"""
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    
    class Meta:
        model = UserGoal
        fields = [
            'id', 'goal_type', 'goal_type_display', 'target_value', 
            'language', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserStreakSerializer(serializers.ModelSerializer):
    """사용자 스트릭 직렬화"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserStreak
        fields = [
            'id', 'username', 'current_streak', 'longest_streak',
            'last_active_date', 'streak_start_date', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'current_streak', 'longest_streak', 
                           'last_active_date', 'streak_start_date', 'updated_at']


class GoalProgressSerializer(serializers.Serializer):
    """목표 진행률 직렬화"""
    goal = UserGoalSerializer()
    current_value = serializers.IntegerField()
    target_value = serializers.IntegerField()
    progress_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_achieved = serializers.BooleanField()
