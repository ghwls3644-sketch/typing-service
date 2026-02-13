"""
데일리 챌린지 자동 생성 Management Command

다음 N일간의 데일리 챌린지를 자동 생성합니다.
중복 생성하지 않으며, 이미 존재하는 날짜는 건너뜁니다.

Usage:
    python manage.py generate_daily_challenge          # 내일 1개
    python manage.py generate_daily_challenge --days 7  # 7일치
    python manage.py generate_daily_challenge --today   # 오늘 것만
"""

import random
from django.core.management.base import BaseCommand
from datetime import date, timedelta

from apps.challenges.models import DailyChallenge


# 챌린지 템플릿: (type, difficulty, title_template, description_template, targets)
CHALLENGE_TEMPLATES = [
    {
        'type': 'speed',
        'difficulty': 1,
        'title': '🚀 속도 도전: 초급',
        'description': '평균 타속 40 WPM 이상을 달성하세요!',
        'target_wpm': 40,
        'target_accuracy': None,
        'target_sessions': 3,
        'reward_points': 50,
    },
    {
        'type': 'speed',
        'difficulty': 2,
        'title': '🚀 속도 도전: 중급',
        'description': '평균 타속 60 WPM 이상을 달성하세요!',
        'target_wpm': 60,
        'target_accuracy': None,
        'target_sessions': 3,
        'reward_points': 100,
    },
    {
        'type': 'speed',
        'difficulty': 3,
        'title': '🚀 속도 도전: 고급',
        'description': '평균 타속 80 WPM 이상을 달성하세요!',
        'target_wpm': 80,
        'target_accuracy': None,
        'target_sessions': 3,
        'reward_points': 200,
    },
    {
        'type': 'accuracy',
        'difficulty': 2,
        'title': '🎯 정확도 마스터',
        'description': '정확도 95% 이상으로 3세션을 완료하세요!',
        'target_wpm': None,
        'target_accuracy': 95.0,
        'target_sessions': 3,
        'reward_points': 100,
    },
    {
        'type': 'accuracy',
        'difficulty': 3,
        'title': '🎯 퍼펙트 타이핑',
        'description': '정확도 98% 이상으로 3세션을 완료하세요!',
        'target_wpm': None,
        'target_accuracy': 98.0,
        'target_sessions': 3,
        'reward_points': 200,
    },
    {
        'type': 'endurance',
        'difficulty': 2,
        'title': '💪 꾸준한 연습',
        'description': '오늘 5번 이상 연습하세요!',
        'target_wpm': None,
        'target_accuracy': None,
        'target_sessions': 5,
        'reward_points': 80,
    },
    {
        'type': 'endurance',
        'difficulty': 3,
        'title': '💪 타자 마라톤',
        'description': '오늘 10번 이상 연습하세요!',
        'target_wpm': None,
        'target_accuracy': None,
        'target_sessions': 10,
        'reward_points': 150,
    },
    {
        'type': 'special',
        'difficulty': 2,
        'title': '⚡ 스피드 + 정확도',
        'description': 'WPM 50 이상, 정확도 93% 이상으로 3세션!',
        'target_wpm': 50,
        'target_accuracy': 93.0,
        'target_sessions': 3,
        'reward_points': 120,
    },
    {
        'type': 'special',
        'difficulty': 4,
        'title': '🔥 극한 챌린지',
        'description': 'WPM 70 이상, 정확도 97% 이상! 최강자만 도전!',
        'target_wpm': 70,
        'target_accuracy': 97.0,
        'target_sessions': 3,
        'reward_points': 300,
    },
]


class Command(BaseCommand):
    help = '데일리 챌린지 자동 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='생성할 일수 (기본: 1)'
        )
        parser.add_argument(
            '--today',
            action='store_true',
            help='오늘의 챌린지만 생성'
        )

    def handle(self, *args, **options):
        days = options['days']
        start_today = options['today']
        
        if start_today:
            start = date.today()
            days = 1
        else:
            # 기본: 내일부터
            start = date.today() + timedelta(days=1)
        
        created_count = 0
        skipped_count = 0
        
        for i in range(days):
            target_date = start + timedelta(days=i)
            
            # 이미 존재하면 스킵
            if DailyChallenge.objects.filter(date=target_date).exists():
                self.stdout.write(f"  ⏭️  {target_date}: 이미 존재")
                skipped_count += 1
                continue
            
            # 랜덤 템플릿 선택
            template = random.choice(CHALLENGE_TEMPLATES)
            
            DailyChallenge.objects.create(
                date=target_date,
                title=template['title'],
                description=template['description'],
                challenge_type=template['type'],
                difficulty=template['difficulty'],
                target_wpm=template['target_wpm'],
                target_accuracy=template['target_accuracy'],
                target_sessions=template['target_sessions'],
                reward_points=template['reward_points'],
                is_active=True,
            )
            
            self.stdout.write(f"  ✅ {target_date}: {template['title']}")
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"\n🎯 완료! 생성: {created_count}개, 건너뜀: {skipped_count}개"
        ))
