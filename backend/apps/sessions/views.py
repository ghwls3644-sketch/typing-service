from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Sum, Count
from django.utils import timezone
from datetime import date
from decimal import Decimal
from .models import TypingSession
from .serializers import (
    TypingSessionSerializer, 
    TypingSessionCreateSerializer,
    TypingSessionListSerializer,
    UserStatsSerializer
)


class TypingSessionViewSet(viewsets.ModelViewSet):
    """타자 세션 API"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = TypingSession.objects.all()
        
        # 로그인한 사용자는 자신의 기록만
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        else:
            # 비로그인 사용자는 guest_session_id로 필터링
            session_id = self.request.query_params.get('guest_session_id')
            if session_id:
                queryset = queryset.filter(guest_session_id=session_id)
            else:
                queryset = queryset.none()
        
        # 필터
        language = self.request.query_params.get('language')
        mode = self.request.query_params.get('mode')
        
        if language:
            queryset = queryset.filter(language=language)
        if mode:
            queryset = queryset.filter(mode=mode)
        
        return queryset.order_by('-started_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TypingSessionCreateSerializer
        if self.action == 'list':
            return TypingSessionListSerializer
        return TypingSessionSerializer
    
    def perform_create(self, serializer):
        session = serializer.save()
        today = timezone.localdate()
        
        if self.request.user.is_authenticated:
            # 로그인 사용자: 기존 UserDaily + UserStreak
            self._update_user_daily_stats(session, today)
            self._update_user_streak(session, today)
        
        if session.guest_session_id:
            # 익명 사용자: ClientDaily + ClientStreak
            self._update_client_daily_stats(session, today)
            self._update_client_streak(session, today)
    
    def _update_user_daily_stats(self, session, today):
        """로그인 사용자 일일 통계 업데이트 (write-through)"""
        from apps.stats.models import UserDaily
        
        user_daily, created = UserDaily.objects.get_or_create(
            user=session.user,
            date=today,
            language=session.language,
            defaults={
                'total_sessions': 0,
                'total_duration_ms': 0,
                'avg_wpm': 0,
                'avg_accuracy': 0,
            }
        )
        
        # 업데이트
        user_daily.total_sessions += 1
        user_daily.total_duration_ms += session.duration_ms
        user_daily.total_chars += session.input_length
        user_daily.total_errors += session.error_count
        
        # 평균 재계산
        sessions_today = TypingSession.objects.filter(
            user=session.user, 
            language=session.language,
            started_at__date=today
        )
        agg = sessions_today.aggregate(
            avg_wpm=Avg('wpm'),
            avg_accuracy=Avg('accuracy'),
            best_wpm=Max('wpm'),
            best_accuracy=Max('accuracy'),
        )
        user_daily.avg_wpm = agg.get('avg_wpm') or 0
        user_daily.avg_accuracy = agg.get('avg_accuracy') or 0
        user_daily.best_wpm = agg.get('best_wpm')
        user_daily.best_accuracy = agg.get('best_accuracy')
        user_daily.save()
    
    def _update_user_streak(self, session, today):
        """로그인 사용자 스트릭 업데이트"""
        from apps.goals.models import UserStreak
        
        streak, created = UserStreak.objects.get_or_create(user=session.user)
        streak.update_streak(today)
    
    def _update_client_daily_stats(self, session, today):
        """익명 사용자 일일 통계 업데이트 (write-through, sum 기반)"""
        from apps.stats.models import ClientDaily
        
        client_daily, created = ClientDaily.objects.get_or_create(
            guest_session_id=session.guest_session_id,
            date=today,
            language=session.language,
            defaults={
                'total_sessions': 0,
                'total_duration_ms': 0,
                'sum_wpm': Decimal('0'),
                'sum_accuracy': Decimal('0'),
                'avg_wpm': Decimal('0'),
                'avg_accuracy': Decimal('0'),
            }
        )
        
        # 누적 업데이트 (re-query 없이 O(1))
        client_daily.total_sessions += 1
        client_daily.total_duration_ms += session.duration_ms
        client_daily.total_chars += session.input_length
        client_daily.total_errors += session.error_count
        client_daily.sum_wpm += session.wpm
        client_daily.sum_accuracy += session.accuracy
        
        # 평균 계산
        if client_daily.total_sessions > 0:
            client_daily.avg_wpm = client_daily.sum_wpm / client_daily.total_sessions
            client_daily.avg_accuracy = client_daily.sum_accuracy / client_daily.total_sessions
        
        # 최고 기록 갱신
        if client_daily.best_wpm is None or session.wpm > client_daily.best_wpm:
            client_daily.best_wpm = session.wpm
        if client_daily.best_accuracy is None or session.accuracy > client_daily.best_accuracy:
            client_daily.best_accuracy = session.accuracy
        
        client_daily.save()
    
    def _update_client_streak(self, session, today):
        """익명 사용자 스트릭 업데이트"""
        from apps.goals.models import ClientStreak
        
        streak, created = ClientStreak.objects.get_or_create(
            guest_session_id=session.guest_session_id
        )
        streak.update_streak(today)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """사용자 통계 조회"""
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'total_sessions': 0,
                'avg_wpm': 0,
                'avg_accuracy': 0,
                'best_wpm': None,
                'total_time_ms': 0,
                'korean_sessions': 0,
                'english_sessions': 0,
            })
        
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            avg_wpm=Avg('wpm'),
            avg_accuracy=Avg('accuracy'),
            best_wpm=Max('wpm'),
            total_time_ms=Sum('duration_ms'),
        )
        
        stats['korean_sessions'] = queryset.filter(language='ko').count()
        stats['english_sessions'] = queryset.filter(language='en').count()
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """최근 기록 조회 (최대 10개)"""
        queryset = self.get_queryset()[:10]
        serializer = TypingSessionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_data(self, request):
        """세션 데이터 JSON 내보내기"""
        guest_id = request.query_params.get('guest_session_id', '')
        
        if request.user.is_authenticated:
            sessions = TypingSession.objects.filter(user=request.user)
        elif guest_id:
            sessions = TypingSession.objects.filter(guest_session_id=guest_id)
        else:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)
        
        export_sessions = []
        for s in sessions.order_by('started_at'):
            export_sessions.append({
                'mode': s.mode,
                'language': s.language,
                'text_content': s.text_content,
                'started_at': s.started_at.isoformat(),
                'duration_ms': s.duration_ms,
                'input_length': s.input_length,
                'correct_length': s.correct_length,
                'error_count': s.error_count,
                'accuracy': float(s.accuracy),
                'wpm': float(s.wpm),
                'cpm': float(s.cpm) if s.cpm else None,
                'guest_session_id': s.guest_session_id,
            })
        
        data = {
            'schema_version': 1,
            'exported_at': timezone.now().isoformat(),
            'guest_session_id': guest_id,
            'total_sessions': len(export_sessions),
            'sessions': export_sessions,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='import')
    def import_data(self, request):
        """세션 데이터 JSON 가져오기 (중복 방지)"""
        import_data = request.data
        
        if not import_data or 'sessions' not in import_data:
            return Response({'detail': 'sessions 필드가 필요합니다.'}, status=400)
        
        guest_id = import_data.get('guest_session_id', '')
        if not request.user.is_authenticated and not guest_id:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)
        
        sessions_data = import_data['sessions']
        imported = 0
        skipped = 0
        errors = 0
        
        from datetime import datetime as dt
        from django.utils.dateparse import parse_datetime
        
        for session_data in sessions_data:
            try:
                started_at = parse_datetime(session_data.get('started_at', ''))
                if not started_at:
                    errors += 1
                    continue
                
                # 중복 체크: guest_session_id + started_at
                dup_filter = {'started_at': started_at}
                if request.user.is_authenticated:
                    dup_filter['user'] = request.user
                else:
                    dup_filter['guest_session_id'] = guest_id
                
                if TypingSession.objects.filter(**dup_filter).exists():
                    skipped += 1
                    continue
                
                # 새 세션 생성
                session = TypingSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    mode=session_data.get('mode', 'practice'),
                    language=session_data.get('language', 'ko'),
                    text_content=session_data.get('text_content', ''),
                    duration_ms=session_data.get('duration_ms', 0),
                    input_length=session_data.get('input_length', 0),
                    correct_length=session_data.get('correct_length', 0),
                    error_count=session_data.get('error_count', 0),
                    accuracy=session_data.get('accuracy', 0),
                    wpm=session_data.get('wpm', 0),
                    cpm=session_data.get('cpm'),
                    guest_session_id=guest_id or session_data.get('guest_session_id', ''),
                )
                
                # started_at 수동 설정 (auto_now_add 우회)
                TypingSession.objects.filter(id=session.id).update(started_at=started_at)
                
                imported += 1
            except Exception:
                errors += 1
                continue
        
        return Response({
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'total': len(sessions_data),
        })

