from rest_framework import serializers
from .models import TypingSession, TypingEvent


class TypingEventSerializer(serializers.ModelSerializer):
    """타이핑 이벤트 직렬화"""
    
    class Meta:
        model = TypingEvent
        fields = ['id', 't_ms', 'expected', 'typed', 'is_correct', 'position']


class TypingSessionSerializer(serializers.ModelSerializer):
    """세션 상세 직렬화"""
    username = serializers.CharField(source='user.username', read_only=True, default='Guest')
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = TypingSession
        fields = [
            'id', 'user', 'username', 'pack', 'text_item', 
            'mode', 'mode_display', 'language', 'language_display', 'text_content',
            'started_at', 'ended_at', 'duration_ms',
            'input_length', 'correct_length', 'error_count',
            'accuracy', 'wpm', 'cpm', 'metadata', 'guest_session_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TypingSessionCreateSerializer(serializers.ModelSerializer):
    """세션 생성 직렬화"""
    events = TypingEventSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = TypingSession
        fields = [
            'pack', 'text_item', 'mode', 'language', 'text_content',
            'started_at', 'ended_at', 'duration_ms',
            'input_length', 'correct_length', 'error_count',
            'accuracy', 'wpm', 'cpm', 'metadata', 'guest_session_id', 'events'
        ]
    
    def create(self, validated_data):
        events_data = validated_data.pop('events', [])
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        session = super().create(validated_data)
        
        # 이벤트 저장 (옵션: 비활성화하려면 이 부분을 주석 처리)
        # for event_data in events_data:
        #     TypingEvent.objects.create(session=session, **event_data)
        
        return session


class TypingSessionListSerializer(serializers.ModelSerializer):
    """세션 목록 직렬화"""
    
    class Meta:
        model = TypingSession
        fields = [
            'id', 'mode', 'language', 'text_content', 
            'wpm', 'accuracy', 'duration_ms', 'started_at'
        ]


class UserStatsSerializer(serializers.Serializer):
    """사용자 통계 직렬화"""
    total_sessions = serializers.IntegerField()
    avg_wpm = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2)
    best_wpm = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    total_time_ms = serializers.IntegerField()
    korean_sessions = serializers.IntegerField()
    english_sessions = serializers.IntegerField()
