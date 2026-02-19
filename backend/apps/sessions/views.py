import logging

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Sum, Count
from django.utils import timezone
from decimal import Decimal
from .models import TypingSession
from .serializers import (
    TypingSessionSerializer,
    TypingSessionCreateSerializer,
    TypingSessionListSerializer,
    UserStatsSerializer
)

logger = logging.getLogger(__name__)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """세션 소유자만 수정/삭제 가능"""

    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 로그인 사용자: 본인 세션만
        if request.user.is_authenticated:
            return obj.user == request.user
        # 게스트: guest_session_id 일치 확인
        guest_id = request.query_params.get(
            'guest_session_id',
            request.data.get('guest_session_id', '')
        )
        return bool(guest_id and obj.guest_session_id == guest_id)


class TypingSessionViewSet(viewsets.ModelViewSet):
    """타자 세션 API"""
    permission_classes = [permissions.AllowAny, IsOwnerOrReadOnly]
    # update/delete는 차단 (세션 기록은 불변 데이터)
    http_method_names = ['get', 'post', 'head', 'options']

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
            # 로그인 사용자: UserDaily + UserStreak
            self._update_user_daily_stats(session, today)
            self._update_user_streak(session, today)
            # 뱃지 획득 체크
            try:
                from apps.achievements.views import check_and_award_badges
                check_and_award_badges(self.request.user)
            except Exception:
                logger.warning("Badge check failed", exc_info=True)
        elif session.guest_session_id:
            # 익명 사용자: ClientDaily + ClientStreak (elif로 이중 집계 방지)
            self._update_client_daily_stats(session, today)
            self._update_client_streak(session, today)

    def _update_user_daily_stats(self, session, today):
        """로그인 사용자 일일 통계 업데이트 (F() 표현식으로 atomic)"""
        from apps.stats.models import UserDaily
        from django.db.models import F, Greatest, Value
        from django.db.models.functions import Coalesce

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

        # F() 표현식으로 atomic 업데이트 (race condition 방지)
        UserDaily.objects.filter(id=user_daily.id).update(
            total_sessions=F('total_sessions') + 1,
            total_duration_ms=F('total_duration_ms') + session.duration_ms,
            total_chars=F('total_chars') + session.input_length,
            total_errors=F('total_errors') + session.error_count,
        )

        # 평균/최고 기록은 aggregate로 재계산 (정확성 보장)
        agg = TypingSession.objects.filter(
            user=session.user,
            language=session.language,
            started_at__date=today
        ).aggregate(
            avg_wpm=Avg('wpm'),
            avg_accuracy=Avg('accuracy'),
            best_wpm=Max('wpm'),
            best_accuracy=Max('accuracy'),
        )
        UserDaily.objects.filter(id=user_daily.id).update(
            avg_wpm=agg.get('avg_wpm') or 0,
            avg_accuracy=agg.get('avg_accuracy') or 0,
            best_wpm=agg.get('best_wpm'),
            best_accuracy=agg.get('best_accuracy'),
        )

    def _update_user_streak(self, session, today):
        """로그인 사용자 스트릭 업데이트"""
        from apps.goals.models import UserStreak

        streak, created = UserStreak.objects.get_or_create(user=session.user)
        streak.update_streak(today)

    def _update_client_daily_stats(self, session, today):
        """익명 사용자 일일 통계 업데이트 (F() 표현식으로 atomic)"""
        from apps.stats.models import ClientDaily
        from django.db.models import F

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

        # F() 표현식으로 atomic 누적 업데이트
        UserDaily_qs = ClientDaily.objects.filter(id=client_daily.id)
        UserDaily_qs.update(
            total_sessions=F('total_sessions') + 1,
            total_duration_ms=F('total_duration_ms') + session.duration_ms,
            total_chars=F('total_chars') + session.input_length,
            total_errors=F('total_errors') + session.error_count,
            sum_wpm=F('sum_wpm') + session.wpm,
            sum_accuracy=F('sum_accuracy') + session.accuracy,
        )

        # DB에서 최신값 다시 읽어 평균/최고 기록 계산
        client_daily.refresh_from_db()
        updates = {}
        if client_daily.total_sessions > 0:
            updates['avg_wpm'] = client_daily.sum_wpm / client_daily.total_sessions
            updates['avg_accuracy'] = client_daily.sum_accuracy / client_daily.total_sessions
        if client_daily.best_wpm is None or session.wpm > client_daily.best_wpm:
            updates['best_wpm'] = session.wpm
        if client_daily.best_accuracy is None or session.accuracy > client_daily.best_accuracy:
            updates['best_accuracy'] = session.accuracy
        if updates:
            ClientDaily.objects.filter(id=client_daily.id).update(**updates)
    
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
    
    MAX_EXPORT_SESSIONS = 5000  # 1회 최대 내보내기 수

    @action(detail=False, methods=['get'], url_path='export')
    def export_data(self, request):
        """세션 데이터 JSON 내보내기 (페이지네이션 지원)"""
        guest_id = request.query_params.get('guest_session_id', '')

        if request.user.is_authenticated:
            sessions = TypingSession.objects.filter(user=request.user)
        elif guest_id:
            sessions = TypingSession.objects.filter(guest_session_id=guest_id)
        else:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)

        # 페이지네이션: offset / limit
        try:
            offset = max(0, int(request.query_params.get('offset', 0)))
        except (ValueError, TypeError):
            offset = 0
        try:
            limit = min(int(request.query_params.get('limit', self.MAX_EXPORT_SESSIONS)),
                        self.MAX_EXPORT_SESSIONS)
        except (ValueError, TypeError):
            limit = self.MAX_EXPORT_SESSIONS

        total_count = sessions.count()
        sessions_page = sessions.order_by('started_at')[offset:offset + limit]

        export_sessions = []
        for s in sessions_page.iterator():
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
            'total_sessions': total_count,
            'offset': offset,
            'limit': limit,
            'has_more': (offset + limit) < total_count,
            'sessions': export_sessions,
        }

        return Response(data)
    
    MAX_IMPORT_SESSIONS = 500  # 1회 최대 임포트 수
    MAX_WPM = 500              # WPM 상한값 (검증용)
    MAX_ACCURACY = 100         # 정확도 상한값

    @action(detail=False, methods=['post'], url_path='import')
    def import_data(self, request):
        """세션 데이터 JSON 가져오기 (중복 방지, 검증 포함)"""
        import_data = request.data

        if not import_data or 'sessions' not in import_data:
            return Response({'detail': 'sessions 필드가 필요합니다.'}, status=400)

        guest_id = import_data.get('guest_session_id', '')
        if not request.user.is_authenticated and not guest_id:
            return Response({'detail': 'guest_session_id 또는 로그인이 필요합니다.'}, status=400)

        sessions_data = import_data['sessions']

        # 크기 제한
        if not isinstance(sessions_data, list):
            return Response({'detail': 'sessions는 배열이어야 합니다.'}, status=400)
        if len(sessions_data) > self.MAX_IMPORT_SESSIONS:
            return Response(
                {'detail': f'최대 {self.MAX_IMPORT_SESSIONS}개까지 가져올 수 있습니다.'},
                status=400
            )

        imported = 0
        skipped = 0
        errors = 0
        error_details = []

        from django.utils.dateparse import parse_datetime

        VALID_MODES = {c[0] for c in TypingSession.MODE_CHOICES}
        VALID_LANGUAGES = {c[0] for c in TypingSession.LANGUAGE_CHOICES}

        for i, session_data in enumerate(sessions_data):
            try:
                if not isinstance(session_data, dict):
                    errors += 1
                    error_details.append(f"[{i}] 잘못된 데이터 형식")
                    continue

                started_at = parse_datetime(session_data.get('started_at', ''))
                if not started_at:
                    errors += 1
                    error_details.append(f"[{i}] started_at 파싱 실패")
                    continue

                # 값 검증
                mode = session_data.get('mode', 'practice')
                language = session_data.get('language', 'ko')
                wpm = session_data.get('wpm', 0)
                accuracy = session_data.get('accuracy', 0)

                if mode not in VALID_MODES:
                    errors += 1
                    error_details.append(f"[{i}] 잘못된 mode: {mode}")
                    continue
                if language not in VALID_LANGUAGES:
                    errors += 1
                    error_details.append(f"[{i}] 잘못된 language: {language}")
                    continue

                try:
                    wpm = float(wpm)
                    accuracy = float(accuracy)
                except (ValueError, TypeError):
                    errors += 1
                    error_details.append(f"[{i}] wpm/accuracy 숫자 변환 실패")
                    continue

                if wpm < 0 or wpm > self.MAX_WPM:
                    errors += 1
                    error_details.append(f"[{i}] WPM 범위 초과: {wpm}")
                    continue
                if accuracy < 0 or accuracy > self.MAX_ACCURACY:
                    errors += 1
                    error_details.append(f"[{i}] accuracy 범위 초과: {accuracy}")
                    continue

                # 중복 체크: user/guest + started_at
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
                    mode=mode,
                    language=language,
                    text_content=session_data.get('text_content', '')[:5000],  # 텍스트 길이 제한
                    duration_ms=max(0, int(session_data.get('duration_ms', 0))),
                    input_length=max(0, int(session_data.get('input_length', 0))),
                    correct_length=max(0, int(session_data.get('correct_length', 0))),
                    error_count=max(0, int(session_data.get('error_count', 0))),
                    accuracy=accuracy,
                    wpm=wpm,
                    cpm=session_data.get('cpm'),
                    guest_session_id=guest_id or session_data.get('guest_session_id', ''),
                )

                # started_at 수동 설정 (auto_now_add 우회)
                TypingSession.objects.filter(id=session.id).update(started_at=started_at)

                imported += 1
            except Exception as e:
                errors += 1
                error_details.append(f"[{i}] 예외: {str(e)}")
                logger.warning(f"Import session error at index {i}: {e}", exc_info=True)
                continue

        return Response({
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'error_details': error_details[:20],  # 에러 상세 최대 20개
            'total': len(sessions_data),
        })

