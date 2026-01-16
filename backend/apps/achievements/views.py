from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Badge, UserBadge, UserLevel
from .serializers import BadgeSerializer, UserBadgeSerializer, UserLevelSerializer, ProfileSerializer


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """뱃지 조회 API"""
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Badge.objects.filter(is_active=True)
        
        # 시크릿 뱃지는 획득한 경우에만 표시
        if self.request.user.is_authenticated:
            owned_badges = UserBadge.objects.filter(user=self.request.user).values_list('badge_id', flat=True)
            queryset = queryset.filter(
                models.Q(is_secret=False) | models.Q(id__in=owned_badges)
            )
        else:
            queryset = queryset.filter(is_secret=False)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """뱃지 카테고리 목록"""
        return Response([
            {'value': c[0], 'label': c[1]} 
            for c in Badge.CATEGORY_CHOICES
        ])


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """사용자 뱃지 API"""
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge')
    
    @action(detail=True, methods=['post'])
    def set_featured(self, request, pk=None):
        """대표 뱃지 설정"""
        user_badge = self.get_object()
        
        # 기존 대표 뱃지 해제
        UserBadge.objects.filter(user=request.user, is_featured=True).update(is_featured=False)
        
        # 새 대표 뱃지 설정
        user_badge.is_featured = True
        user_badge.save()
        
        return Response({'message': '대표 뱃지가 설정되었습니다.'})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """대표 뱃지 목록"""
        featured = self.get_queryset().filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class UserLevelViewSet(viewsets.ViewSet):
    """사용자 레벨 API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """내 레벨 정보"""
        user_level, created = UserLevel.objects.get_or_create(user=request.user)
        serializer = UserLevelSerializer(user_level)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """프로필 전체 정보"""
        user_level, _ = UserLevel.objects.get_or_create(user=request.user)
        badges = UserBadge.objects.filter(user=request.user).select_related('badge')
        featured_badges = badges.filter(is_featured=True)[:3]
        
        data = {
            'level_info': UserLevelSerializer(user_level).data,
            'badges': UserBadgeSerializer(badges, many=True).data,
            'badges_count': badges.count(),
            'featured_badges': UserBadgeSerializer(featured_badges, many=True).data,
        }
        
        return Response(data)


# 뱃지 획득 로직 (signals 또는 별도 서비스에서 호출)
def check_and_award_badges(user):
    """뱃지 획득 조건 체크 및 자동 부여"""
    from apps.sessions.models import TypingSession
    from apps.goals.models import UserStreak
    from django.db.models import Avg, Max, Count
    
    # 사용자 통계
    stats = TypingSession.objects.filter(user=user).aggregate(
        avg_wpm=Avg('wpm'),
        max_wpm=Max('wpm'),
        avg_accuracy=Avg('accuracy'),
        max_accuracy=Max('accuracy'),
        total_sessions=Count('id'),
    )
    
    streak = UserStreak.objects.filter(user=user).first()
    current_streak = streak.current_streak if streak else 0
    
    # 조건별 뱃지 체크
    conditions_to_check = [
        ('wpm_reach', stats.get('max_wpm') or 0),
        ('accuracy_reach', stats.get('max_accuracy') or 0),
        ('sessions_complete', stats.get('total_sessions') or 0),
        ('streak_reach', current_streak),
    ]
    
    awarded = []
    for condition_type, current_value in conditions_to_check:
        badges = Badge.objects.filter(
            condition_type=condition_type,
            condition_value__lte=current_value,
            is_active=True
        ).exclude(
            id__in=UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        )
        
        for badge in badges:
            UserBadge.objects.create(user=user, badge=badge)
            awarded.append(badge)
            
            # 레벨 시스템에 포인트 추가
            user_level, _ = UserLevel.objects.get_or_create(user=user)
            user_level.add_points(badge.reward_points)
            user_level.add_experience(badge.reward_points // 2)
    
    return awarded


# models import for Q object
from django.db import models
