from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import date
from .models import DailyChallenge, UserChallenge
from .serializers import (
    DailyChallengeSerializer, 
    UserChallengeSerializer,
    UserChallengeJoinSerializer,
    UserChallengeProgressSerializer
)


class DailyChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """데일리 챌린지 API"""
    serializer_class = DailyChallengeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return DailyChallenge.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """오늘의 챌린지 조회"""
        today = date.today()
        challenge = self.get_queryset().filter(date=today).first()
        
        if not challenge:
            return Response({'detail': '오늘의 챌린지가 없습니다.'}, status=404)
        
        serializer = self.get_serializer(challenge)
        data = serializer.data
        
        # 현재 사용자의 참가 상태
        if request.user.is_authenticated:
            user_challenge = UserChallenge.objects.filter(
                user=request.user, challenge=challenge
            ).first()
            if user_challenge:
                data['my_progress'] = UserChallengeProgressSerializer(user_challenge).data
        
        return Response(data)


class UserChallengeViewSet(viewsets.ModelViewSet):
    """사용자 챌린지 API"""
    serializer_class = UserChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        """챌린지 참가"""
        serializer = UserChallengeJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        
        try:
            challenge = DailyChallenge.objects.get(id=challenge_id, is_active=True)
        except DailyChallenge.DoesNotExist:
            return Response({'detail': '챌린지를 찾을 수 없습니다.'}, status=404)
        
        # 이미 참가 중인지 확인
        existing = UserChallenge.objects.filter(
            user=request.user, challenge=challenge
        ).first()
        
        if existing:
            return Response(
                UserChallengeSerializer(existing).data,
                status=status.HTTP_200_OK
            )
        
        # 새로 참가
        user_challenge = UserChallenge.objects.create(
            user=request.user,
            challenge=challenge
        )
        
        return Response(
            UserChallengeSerializer(user_challenge).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def claim_reward(self, request, pk=None):
        """보상 수령"""
        user_challenge = self.get_object()
        
        if user_challenge.status != 'completed':
            return Response({'detail': '챌린지를 먼저 완료해야 합니다.'}, status=400)
        
        if user_challenge.reward_claimed:
            return Response({'detail': '이미 보상을 수령했습니다.'}, status=400)
        
        # 보상 지급
        user_challenge.reward_claimed = True
        user_challenge.save()
        
        # 포인트/경험치 추가 (UserLevel 연동)
        from apps.achievements.models import UserLevel
        user_level, _ = UserLevel.objects.get_or_create(user=request.user)
        user_level.add_points(user_challenge.challenge.reward_points)
        user_level.add_experience(user_challenge.challenge.reward_points // 2)
        
        return Response({
            'message': '보상을 수령했습니다!',
            'reward_points': user_challenge.challenge.reward_points,
            'new_level': user_level.level,
            'new_experience': user_level.experience,
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """현재 진행 중인 챌린지"""
        challenges = self.get_queryset().filter(status='in_progress')
        serializer = UserChallengeProgressSerializer(challenges, many=True)
        return Response(serializer.data)
