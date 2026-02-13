from rest_framework import serializers
from .models import Snapshot, Entry


class EntrySerializer(serializers.ModelSerializer):
    """랭킹 엔트리 직렬화"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Entry
        fields = [
            'id', 'rank', 'name', 'display_name', 'score_wpm', 'score_accuracy',
            'session_count', 'best_wpm', 'total_duration_ms'
        ]
    
    def get_name(self, obj):
        if obj.user:
            return obj.user.nickname or obj.user.username
        return obj.display_name


class SnapshotSerializer(serializers.ModelSerializer):
    """랭킹 스냅샷 직렬화"""
    entry_count = serializers.IntegerField(read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    
    class Meta:
        model = Snapshot
        fields = [
            'id', 'period', 'period_display', 'start_date', 'end_date',
            'mode', 'language', 'entry_count', 'generated_at', 'is_active'
        ]


class SnapshotDetailSerializer(serializers.ModelSerializer):
    """랭킹 스냅샷 상세 직렬화 (엔트리 포함)"""
    entries = EntrySerializer(many=True, read_only=True)
    entry_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Snapshot
        fields = [
            'id', 'period', 'start_date', 'end_date', 'mode', 'language',
            'entry_count', 'generated_at', 'entries'
        ]


class MyRankSerializer(serializers.Serializer):
    """내 순위 정보 직렬화"""
    snapshot = SnapshotSerializer()
    my_entry = EntrySerializer(allow_null=True)
    neighbors = EntrySerializer(many=True)
