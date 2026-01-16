from rest_framework import serializers
from .models import DailyChallenge, UserChallenge


class DailyChallengeSerializer(serializers.ModelSerializer):
    """데일리 챌린지 직렬화"""
    challenge_type_display = serializers.CharField(source='get_challenge_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    participants_count = serializers.SerializerMethodField()
    completed_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyChallenge
        fields = [
            'id', 'date', 'title', 'description',
            'challenge_type', 'challenge_type_display',
            'difficulty', 'difficulty_display',
            'target_wpm', 'target_accuracy', 'target_sessions', 'target_time_minutes',
            'text_pack', 'reward_points', 'reward_badge',
            'participants_count', 'completed_count', 'is_active'
        ]
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_completed_count(self, obj):
        return obj.participants.filter(status='completed').count()


class UserChallengeSerializer(serializers.ModelSerializer):
    """사용자 챌린지 직렬화"""
    challenge = DailyChallengeSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserChallenge
        fields = [
            'id', 'challenge', 'status', 'status_display',
            'current_wpm', 'current_accuracy', 'current_sessions', 'current_time_minutes',
            'reward_claimed', 'started_at', 'completed_at'
        ]


class UserChallengeJoinSerializer(serializers.Serializer):
    """챌린지 참가 직렬화"""
    challenge_id = serializers.IntegerField()


class UserChallengeProgressSerializer(serializers.ModelSerializer):
    """챌린지 진행률 직렬화"""
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    target_wpm = serializers.IntegerField(source='challenge.target_wpm', read_only=True)
    target_accuracy = serializers.DecimalField(source='challenge.target_accuracy', max_digits=5, decimal_places=2, read_only=True)
    target_sessions = serializers.IntegerField(source='challenge.target_sessions', read_only=True)
    
    progress_wpm = serializers.SerializerMethodField()
    progress_accuracy = serializers.SerializerMethodField()
    progress_sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserChallenge
        fields = [
            'id', 'challenge_title', 'status',
            'current_wpm', 'target_wpm', 'progress_wpm',
            'current_accuracy', 'target_accuracy', 'progress_accuracy',
            'current_sessions', 'target_sessions', 'progress_sessions',
        ]
    
    def get_progress_wpm(self, obj):
        if not obj.challenge.target_wpm:
            return 100
        return min(((obj.current_wpm or 0) / obj.challenge.target_wpm) * 100, 100)
    
    def get_progress_accuracy(self, obj):
        if not obj.challenge.target_accuracy:
            return 100
        return min((float(obj.current_accuracy or 0) / float(obj.challenge.target_accuracy)) * 100, 100)
    
    def get_progress_sessions(self, obj):
        if not obj.challenge.target_sessions:
            return 100
        return min((obj.current_sessions / obj.challenge.target_sessions) * 100, 100)
