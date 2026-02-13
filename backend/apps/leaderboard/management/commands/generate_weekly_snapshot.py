"""
주간 랭킹 스냅샷 생성 Management Command

지난 1주간의 practice/ranked 세션 데이터를 집계하여
leaderboard Snapshot + Entry를 생성합니다.

Usage:
    python manage.py generate_weekly_snapshot
    python manage.py generate_weekly_snapshot --language ko
    python manage.py generate_weekly_snapshot --min-sessions 3
"""

from django.core.management.base import BaseCommand
from django.db.models import Avg, Max, Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.leaderboard.models import Snapshot, Entry
from apps.sessions.models import TypingSession


class Command(BaseCommand):
    help = '주간 랭킹 스냅샷 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            default='all',
            choices=['ko', 'en', 'all'],
            help='언어 필터 (기본: all)'
        )
        parser.add_argument(
            '--min-sessions',
            type=int,
            default=3,
            help='최소 세션 수 (기본: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 저장 없이 결과만 출력'
        )

    def handle(self, *args, **options):
        language = options['language']
        min_sessions = options['min_sessions']
        dry_run = options['dry_run']

        today = timezone.localdate()
        # 이번 주 월요일 ~ 일요일 (지난 주 기준)
        end_date = today - timedelta(days=today.weekday())  # 이번 주 월요일
        start_date = end_date - timedelta(days=7)  # 지난 주 월요일
        end_date = end_date - timedelta(days=1)  # 지난 주 일요일

        self.stdout.write(f"\n📊 주간 랭킹 스냅샷 생성")
        self.stdout.write(f"   기간: {start_date} ~ {end_date}")
        self.stdout.write(f"   언어: {language}")
        self.stdout.write(f"   최소 세션: {min_sessions}회\n")

        # 기존 스냅샷 확인
        existing = Snapshot.objects.filter(
            period='weekly',
            start_date=start_date,
            end_date=end_date,
            mode='all',
            language=language
        ).first()

        if existing:
            self.stdout.write(self.style.WARNING(
                f"⚠️  이미 스냅샷 존재 (ID: {existing.id}). 기존 데이터 삭제 후 재생성."
            ))
            if not dry_run:
                existing.entries.all().delete()
                existing.delete()

        # practice + ranked 모드 세션 집계
        base_qs = TypingSession.objects.filter(
            mode__in=['practice', 'ranked'],
            started_at__date__gte=start_date,
            started_at__date__lte=end_date,
        )

        if language != 'all':
            base_qs = base_qs.filter(language=language)

        # --- 로그인 사용자 집계 ---
        user_stats = (
            base_qs
            .filter(user__isnull=False)
            .values('user_id', 'user__username', 'user__nickname')
            .annotate(
                avg_wpm=Avg('wpm'),
                avg_accuracy=Avg('accuracy'),
                best_wpm=Max('wpm'),
                session_count=Count('id'),
                total_duration_ms=Sum('duration_ms'),
            )
            .filter(session_count__gte=min_sessions)
        )

        # --- 익명 사용자 집계 ---
        guest_stats = (
            base_qs
            .filter(user__isnull=True, guest_session_id__gt='')
            .values('guest_session_id')
            .annotate(
                avg_wpm=Avg('wpm'),
                avg_accuracy=Avg('accuracy'),
                best_wpm=Max('wpm'),
                session_count=Count('id'),
                total_duration_ms=Sum('duration_ms'),
            )
            .filter(session_count__gte=min_sessions)
        )

        # 통합 정렬: avg_wpm DESC
        combined = []

        for row in user_stats:
            combined.append({
                'user_id': row['user_id'],
                'guest_session_id': '',
                'display_name': row['user__nickname'] or row['user__username'],
                'avg_wpm': row['avg_wpm'],
                'avg_accuracy': row['avg_accuracy'],
                'best_wpm': row['best_wpm'],
                'session_count': row['session_count'],
                'total_duration_ms': row['total_duration_ms'],
            })

        for row in guest_stats:
            gid = row['guest_session_id']
            # 익명 사용자 표시 이름: Guest_XXXX (마지막 4자)
            display_name = f"Guest_{gid[-4:]}" if len(gid) >= 4 else "Guest"
            combined.append({
                'user_id': None,
                'guest_session_id': gid,
                'display_name': display_name,
                'avg_wpm': row['avg_wpm'],
                'avg_accuracy': row['avg_accuracy'],
                'best_wpm': row['best_wpm'],
                'session_count': row['session_count'],
                'total_duration_ms': row['total_duration_ms'],
            })

        # WPM 기준 내림차순 정렬
        combined.sort(key=lambda x: float(x['avg_wpm'] or 0), reverse=True)

        self.stdout.write(f"   참가자: {len(combined)}명\n")

        if not combined:
            self.stdout.write(self.style.WARNING("   ⚠️  조건을 만족하는 참가자가 없습니다.\n"))
            return

        if dry_run:
            for i, row in enumerate(combined[:20], 1):
                self.stdout.write(
                    f"   #{i:3d} {row['display_name']:20s} "
                    f"WPM={float(row['avg_wpm']):.1f}  "
                    f"ACC={float(row['avg_accuracy']):.1f}%  "
                    f"세션={row['session_count']}"
                )
            if len(combined) > 20:
                self.stdout.write(f"   ... 외 {len(combined)-20}명")
            return

        # 스냅샷 생성
        snapshot = Snapshot.objects.create(
            period='weekly',
            start_date=start_date,
            end_date=end_date,
            mode='all',
            language=language,
            is_active=True,
        )

        # 엔트리 생성
        entries = []
        for rank, row in enumerate(combined, 1):
            entries.append(Entry(
                snapshot=snapshot,
                user_id=row['user_id'],
                guest_session_id=row['guest_session_id'],
                display_name=row['display_name'],
                rank=rank,
                score_wpm=Decimal(str(round(float(row['avg_wpm']), 2))),
                score_accuracy=Decimal(str(round(float(row['avg_accuracy']), 2))),
                session_count=row['session_count'],
                best_wpm=Decimal(str(round(float(row['best_wpm']), 2))) if row['best_wpm'] else None,
                total_duration_ms=row['total_duration_ms'] or 0,
            ))
        
        Entry.objects.bulk_create(entries)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ 스냅샷 생성 완료! (ID: {snapshot.id}, 엔트리: {len(entries)}개)\n"
        ))

        # 상위 10명 출력
        for entry in entries[:10]:
            self.stdout.write(
                f"   #{entry.rank:3d} {entry.display_name:20s} "
                f"WPM={float(entry.score_wpm):.1f}  "
                f"ACC={float(entry.score_accuracy):.1f}%"
            )
