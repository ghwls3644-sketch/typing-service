"""
뱃지 시드 데이터 생성 Management Command

게임 진행에 필요한 기본 뱃지를 생성합니다.
이미 존재하는 code는 건너뜁니다.

Usage:
    python manage.py seed_badges
"""

from django.core.management.base import BaseCommand
from apps.achievements.models import Badge


BADGE_SEEDS = [
    # === 속도 뱃지 ===
    {
        'code': 'speed_beginner',
        'name': '타자 입문자',
        'description': 'WPM 30 이상을 달성하세요!',
        'icon': '🐢',
        'category': 'speed',
        'rarity': 1,
        'condition_type': 'wpm_reach',
        'condition_value': 30,
        'reward_points': 30,
        'order': 1,
    },
    {
        'code': 'speed_intermediate',
        'name': '타자 숙련자',
        'description': 'WPM 50 이상을 달성하세요!',
        'icon': '🐇',
        'category': 'speed',
        'rarity': 1,
        'condition_type': 'wpm_reach',
        'condition_value': 50,
        'reward_points': 50,
        'order': 2,
    },
    {
        'code': 'speed_advanced',
        'name': '타자 고수',
        'description': 'WPM 80 이상을 달성하세요!',
        'icon': '🦅',
        'category': 'speed',
        'rarity': 2,
        'condition_type': 'wpm_reach',
        'condition_value': 80,
        'reward_points': 100,
        'order': 3,
    },
    {
        'code': 'speed_master',
        'name': '타자 마스터',
        'description': 'WPM 120 이상을 달성하세요!',
        'icon': '⚡',
        'category': 'speed',
        'rarity': 3,
        'condition_type': 'wpm_reach',
        'condition_value': 120,
        'reward_points': 200,
        'order': 4,
    },
    {
        'code': 'speed_legend',
        'name': '전설의 타자',
        'description': 'WPM 150 이상을 달성하세요!',
        'icon': '🔥',
        'category': 'speed',
        'rarity': 4,
        'condition_type': 'wpm_reach',
        'condition_value': 150,
        'reward_points': 500,
        'order': 5,
        'is_secret': True,
    },
    
    # === 정확도 뱃지 ===
    {
        'code': 'accuracy_90',
        'name': '90% 정확도',
        'description': '정확도 90% 이상을 달성하세요!',
        'icon': '🎯',
        'category': 'accuracy',
        'rarity': 1,
        'condition_type': 'accuracy_reach',
        'condition_value': 90,
        'reward_points': 30,
        'order': 10,
    },
    {
        'code': 'accuracy_95',
        'name': '95% 정확도',
        'description': '정확도 95% 이상을 달성하세요!',
        'icon': '💎',
        'category': 'accuracy',
        'rarity': 2,
        'condition_type': 'accuracy_reach',
        'condition_value': 95,
        'reward_points': 80,
        'order': 11,
    },
    {
        'code': 'accuracy_99',
        'name': '퍼펙트 타이핑',
        'description': '정확도 99% 이상을 달성하세요!',
        'icon': '👑',
        'category': 'accuracy',
        'rarity': 3,
        'condition_type': 'accuracy_reach',
        'condition_value': 99,
        'reward_points': 200,
        'order': 12,
    },
    
    # === 연속일 뱃지 ===
    {
        'code': 'streak_3',
        'name': '3일 연속',
        'description': '3일 연속으로 연습하세요!',
        'icon': '📅',
        'category': 'streak',
        'rarity': 1,
        'condition_type': 'streak_reach',
        'condition_value': 3,
        'reward_points': 30,
        'order': 20,
    },
    {
        'code': 'streak_7',
        'name': '1주일 연속',
        'description': '7일 연속으로 연습하세요!',
        'icon': '🔥',
        'category': 'streak',
        'rarity': 2,
        'condition_type': 'streak_reach',
        'condition_value': 7,
        'reward_points': 80,
        'order': 21,
    },
    {
        'code': 'streak_30',
        'name': '30일 연속!',
        'description': '30일 연속으로 연습하세요!',
        'icon': '🏆',
        'category': 'streak',
        'rarity': 3,
        'condition_type': 'streak_reach',
        'condition_value': 30,
        'reward_points': 300,
        'order': 22,
    },
    {
        'code': 'streak_100',
        'name': '100일 연속!!',
        'description': '100일 연속으로 연습하세요! 전설의 의지!',
        'icon': '💫',
        'category': 'streak',
        'rarity': 4,
        'condition_type': 'streak_reach',
        'condition_value': 100,
        'reward_points': 1000,
        'order': 23,
        'is_secret': True,
    },
    
    # === 마일스톤 뱃지 ===
    {
        'code': 'sessions_10',
        'name': '10세션 달성',
        'description': '총 10번의 연습 세션을 완료하세요!',
        'icon': '🌱',
        'category': 'milestone',
        'rarity': 1,
        'condition_type': 'sessions_complete',
        'condition_value': 10,
        'reward_points': 30,
        'order': 30,
    },
    {
        'code': 'sessions_50',
        'name': '50세션 달성',
        'description': '총 50번의 연습 세션을 완료하세요!',
        'icon': '🌿',
        'category': 'milestone',
        'rarity': 1,
        'condition_type': 'sessions_complete',
        'condition_value': 50,
        'reward_points': 80,
        'order': 31,
    },
    {
        'code': 'sessions_100',
        'name': '100세션 달성',
        'description': '총 100번의 연습 세션을 완료하세요!',
        'icon': '🌳',
        'category': 'milestone',
        'rarity': 2,
        'condition_type': 'sessions_complete',
        'condition_value': 100,
        'reward_points': 150,
        'order': 32,
    },
    {
        'code': 'sessions_500',
        'name': '500세션 달성',
        'description': '총 500번의 연습을! 진정한 타자 마니아!',
        'icon': '🏔️',
        'category': 'milestone',
        'rarity': 3,
        'condition_type': 'sessions_complete',
        'condition_value': 500,
        'reward_points': 500,
        'order': 33,
    },
    
    # === 챌린지 뱃지 ===
    {
        'code': 'challenge_first',
        'name': '첫 챌린지',
        'description': '첫 데일리 챌린지를 완료하세요!',
        'icon': '⭐',
        'category': 'challenge',
        'rarity': 1,
        'condition_type': 'challenge_complete',
        'condition_value': 1,
        'reward_points': 50,
        'order': 40,
    },
    {
        'code': 'challenge_10',
        'name': '챌린지 10회',
        'description': '10개의 데일리 챌린지를 완료하세요!',
        'icon': '🌟',
        'category': 'challenge',
        'rarity': 2,
        'condition_type': 'challenge_complete',
        'condition_value': 10,
        'reward_points': 150,
        'order': 41,
    },
]


class Command(BaseCommand):
    help = '뱃지 시드 데이터 생성'

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        
        for seed in BADGE_SEEDS:
            code = seed['code']
            if Badge.objects.filter(code=code).exists():
                skipped += 1
                continue
            
            Badge.objects.create(**seed)
            self.stdout.write(f"  ✅ {seed['icon']} {seed['name']} ({code})")
            created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"\n🏆 완료! 생성: {created}개, 건너뜀: {skipped}개"
        ))
