from rest_framework import serializers
from .models import UserDaily, ClientDaily


class UserDailySerializer(serializers.ModelSerializer):
    """일일 통계 직렬화"""
    username = serializers.CharField(source='user.username', read_only=True)
    total_duration_minutes = serializers.DecimalField(
        source='total_duration_minutes', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = UserDaily
        fields = [
            'id', 'user', 'username', 'date', 'language',
            'total_sessions', 'total_duration_ms', 'total_duration_minutes',
            'avg_wpm', 'avg_accuracy', 'best_wpm', 'best_accuracy',
            'total_chars', 'total_errors', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserDailyListSerializer(serializers.ModelSerializer):
    """일일 통계 목록용 직렬화"""
    
    class Meta:
        model = UserDaily
        fields = ['date', 'language', 'total_sessions', 'avg_wpm', 'avg_accuracy', 'best_wpm']


class ClientDailySerializer(serializers.ModelSerializer):
    """익명 일일 통계 직렬화"""
    total_duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientDaily
        fields = [
            'date', 'language',
            'total_sessions', 'total_duration_ms', 'total_duration_minutes',
            'avg_wpm', 'avg_accuracy', 'best_wpm', 'best_accuracy',
            'total_chars', 'total_errors'
        ]
    
    def get_total_duration_minutes(self, obj):
        return round(obj.total_duration_ms / 60000, 2)


class StatsOverviewSerializer(serializers.Serializer):
    """통계 요약 직렬화 (로그인/익명 공용)"""
    total_sessions = serializers.IntegerField()
    total_duration_ms = serializers.IntegerField()
    avg_wpm = serializers.DecimalField(max_digits=6, decimal_places=2)
    avg_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2)
    best_wpm = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    today_sessions = serializers.IntegerField(default=0)
    today_duration_ms = serializers.IntegerField(default=0)
    today_avg_wpm = serializers.DecimalField(max_digits=6, decimal_places=2, default=0)
    today_avg_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
