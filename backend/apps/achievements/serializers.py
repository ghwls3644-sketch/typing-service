from rest_framework import serializers
from .models import Badge, UserBadge, UserLevel


class BadgeSerializer(serializers.ModelSerializer):
    """뱃지 직렬화"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)
    
    class Meta:
        model = Badge
        fields = [
            'id', 'code', 'name', 'description', 'icon',
            'category', 'category_display', 'rarity', 'rarity_display',
            'reward_points', 'is_secret', 'order'
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    """사용자 뱃지 직렬화"""
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at', 'is_featured']


class UserLevelSerializer(serializers.ModelSerializer):
    """사용자 레벨 직렬화"""
    username = serializers.CharField(source='user.username', read_only=True)
    exp_to_next_level = serializers.IntegerField(read_only=True)
    progress_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = UserLevel
        fields = [
            'level', 'experience', 'exp_to_next_level', 'progress_percent',
            'total_points', 'username'
        ]


class ProfileSerializer(serializers.Serializer):
    """사용자 프로필 직렬화"""
    level_info = UserLevelSerializer()
    badges = UserBadgeSerializer(many=True)
    badges_count = serializers.IntegerField()
    featured_badges = UserBadgeSerializer(many=True)
