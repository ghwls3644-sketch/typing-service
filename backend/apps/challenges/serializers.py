from rest_framework import serializers
from .models import DailyChallenge, UserChallenge, ClientChallenge


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
        user_count = obj.participants.count()
        guest_count = obj.guest_participants.count()
        return user_count + guest_count
    
    def get_completed_count(self, obj):
        user_done = obj.participants.filter(status='completed').count()
        guest_done = obj.guest_participants.filter(status='completed').count()
        return user_done + guest_done


class ChallengeProgressSerializer(serializers.Serializer):
    """챌린지 진행률 직렬화 (로그인/익명 공용)"""
    id = serializers.IntegerField()
    challenge_title = serializers.CharField()
    status = serializers.CharField()
    current_wpm = serializers.IntegerField(allow_null=True)
    target_wpm = serializers.IntegerField(allow_null=True)
    progress_wpm = serializers.FloatField()
    current_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    target_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    progress_accuracy = serializers.FloatField()
    current_sessions = serializers.IntegerField()
    target_sessions = serializers.IntegerField(allow_null=True)
    progress_sessions = serializers.FloatField()


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


class ClientChallengeSerializer(serializers.ModelSerializer):
    """익명 챌린지 직렬화"""
    challenge = DailyChallengeSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ClientChallenge
        fields = [
            'id', 'challenge', 'status', 'status_display',
            'current_wpm', 'current_accuracy', 'current_sessions', 'current_time_minutes',
            'started_at', 'completed_at'
        ]


class UserChallengeJoinSerializer(serializers.Serializer):
    """챌린지 참가 직렬화"""
    challenge_id = serializers.IntegerField()
    guest_session_id = serializers.CharField(required=False, allow_blank=True, default='')


def build_progress_data(record):
    """UserChallenge/ClientChallenge → 진행률 dict 변환"""
    c = record.challenge
    
    def pct(current, target):
        if not target:
            return 100.0
        return min((float(current or 0) / float(target)) * 100, 100.0)
    
    return {
        'id': record.id,
        'challenge_title': c.title,
        'status': record.status,
        'current_wpm': record.current_wpm,
        'target_wpm': c.target_wpm,
        'progress_wpm': pct(record.current_wpm, c.target_wpm),
        'current_accuracy': record.current_accuracy,
        'target_accuracy': c.target_accuracy,
        'progress_accuracy': pct(record.current_accuracy, c.target_accuracy),
        'current_sessions': record.current_sessions,
        'target_sessions': c.target_sessions,
        'progress_sessions': pct(record.current_sessions, c.target_sessions),
    }
