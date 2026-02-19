from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import DailyChallenge, UserChallenge, ClientChallenge
from .serializers import (
    DailyChallengeSerializer, 
    UserChallengeSerializer,
    ClientChallengeSerializer,
    UserChallengeJoinSerializer,
    ChallengeProgressSerializer,
    build_progress_data
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
        today = timezone.localdate()
        challenge = self.get_queryset().filter(date=today).first()
        
        if not challenge:
            return Response({'detail': '오늘의 챌린지가 없습니다.'}, status=404)
        
        serializer = self.get_serializer(challenge)
        data = serializer.data
        
        # 현재 사용자의 참가 상태
        if request.user.is_authenticated:
            record = UserChallenge.objects.filter(
                user=request.user, challenge=challenge
            ).first()
            if record:
                data['my_progress'] = build_progress_data(record)
        else:
            guest_id = request.query_params.get('guest_session_id', '')
            if guest_id:
                record = ClientChallenge.objects.filter(
                    guest_session_id=guest_id, challenge=challenge
                ).first()
                if record:
                    data['my_progress'] = build_progress_data(record)
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        """챌린지 참가 (로그인/익명 모두)"""
        serializer = UserChallengeJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        guest_id = serializer.validated_data.get('guest_session_id', '')
        
        try:
            challenge = DailyChallenge.objects.get(id=challenge_id, is_active=True)
        except DailyChallenge.DoesNotExist:
            return Response({'detail': '챌린지를 찾을 수 없습니다.'}, status=404)
        
        if request.user.is_authenticated:
            record, created = UserChallenge.objects.get_or_create(
                user=request.user, challenge=challenge
            )
            resp_serializer = UserChallengeSerializer(record)
        elif guest_id:
            record, created = ClientChallenge.objects.get_or_create(
                guest_session_id=guest_id, challenge=challenge
            )
            resp_serializer = ClientChallengeSerializer(record)
        else:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)
        
        return Response(
            resp_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    MAX_WPM = 500       # 합리적인 WPM 상한값
    MAX_ACCURACY = 100  # 정확도 상한값

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """챌린지 결과 제출 (서버 측 검증 포함)"""
        challenge_id = request.data.get('challenge_id')
        guest_id = request.data.get('guest_session_id', '')
        wpm = request.data.get('wpm')
        accuracy = request.data.get('accuracy')

        if not challenge_id:
            return Response({'detail': 'challenge_id 필수'}, status=400)

        # WPM/accuracy 서버 측 검증
        if wpm is not None:
            try:
                wpm = int(wpm)
            except (ValueError, TypeError):
                return Response({'detail': 'wpm은 정수여야 합니다.'}, status=400)
            if wpm < 0 or wpm > self.MAX_WPM:
                return Response(
                    {'detail': f'wpm은 0~{self.MAX_WPM} 범위여야 합니다.'},
                    status=400
                )
        if accuracy is not None:
            try:
                accuracy = float(accuracy)
            except (ValueError, TypeError):
                return Response({'detail': 'accuracy는 숫자여야 합니다.'}, status=400)
            if accuracy < 0 or accuracy > self.MAX_ACCURACY:
                return Response(
                    {'detail': f'accuracy는 0~{self.MAX_ACCURACY} 범위여야 합니다.'},
                    status=400
                )
        
        try:
            challenge = DailyChallenge.objects.get(id=challenge_id, is_active=True)
        except DailyChallenge.DoesNotExist:
            return Response({'detail': '챌린지를 찾을 수 없습니다.'}, status=404)
        
        # 참가 기록 찾기/만들기
        if request.user.is_authenticated:
            record, _ = UserChallenge.objects.get_or_create(
                user=request.user, challenge=challenge
            )
        elif guest_id:
            record, _ = ClientChallenge.objects.get_or_create(
                guest_session_id=guest_id, challenge=challenge
            )
        else:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)
        
        # 진행 상황 업데이트 (최고 기록으로)
        record.current_sessions += 1
        if wpm and (record.current_wpm is None or int(wpm) > record.current_wpm):
            record.current_wpm = int(wpm)
        if accuracy and (record.current_accuracy is None or float(accuracy) > float(record.current_accuracy)):
            record.current_accuracy = accuracy
        record.save()
        
        # 완료 체크
        completed = record.check_completion()
        
        progress = build_progress_data(record)
        progress['just_completed'] = completed and record.status == 'completed'
        
        return Response(progress)
    
    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """오늘의 챌린지 랭킹 (WPM 기준)"""
        today = timezone.localdate()
        challenge = self.get_queryset().filter(date=today).first()
        
        if not challenge:
            return Response({'detail': '오늘의 챌린지가 없습니다.'}, status=404)
        
        # 로그인 사용자 + 익명 사용자 합산 랭킹
        entries = []
        
        for uc in challenge.participants.select_related('user').filter(current_wpm__isnull=False).order_by('-current_wpm'):
            entries.append({
                'name': uc.user.nickname or uc.user.username,
                'wpm': uc.current_wpm,
                'accuracy': float(uc.current_accuracy or 0),
                'sessions': uc.current_sessions,
                'status': uc.status,
            })
        
        for cc in challenge.guest_participants.filter(current_wpm__isnull=False).order_by('-current_wpm'):
            gid = cc.guest_session_id
            entries.append({
                'name': f"Guest_{gid[-4:]}" if len(gid) >= 4 else "Guest",
                'wpm': cc.current_wpm,
                'accuracy': float(cc.current_accuracy or 0),
                'sessions': cc.current_sessions,
                'status': cc.status,
            })
        
        # WPM 기준 정렬
        entries.sort(key=lambda x: x['wpm'], reverse=True)
        
        # 순위 부여
        for i, entry in enumerate(entries, 1):
            entry['rank'] = i
        
        return Response({
            'challenge': DailyChallengeSerializer(challenge).data,
            'ranking': entries[:50],
            'total_participants': len(entries),
        })


class UserChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """사용자 챌린지 기록 API (로그인 사용자)"""
    serializer_class = UserChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """현재 진행 중인 챌린지"""
        challenges = self.get_queryset().filter(status='in_progress')
        serializer = UserChallengeSerializer(challenges, many=True)
        return Response(serializer.data)
