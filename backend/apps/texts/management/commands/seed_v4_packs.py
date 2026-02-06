"""
v4.0 팩 시드 커맨드 - 12개 팩 자동 생성
Usage: python manage.py seed_v4_packs
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack


# 팩 정의: (code, language, kind, theme, difficulty, title, description)
PACK_DEFINITIONS = [
    # 한글 단어 팩 (6개)
    ('ko-word-daily-1', 'ko', 'word', 'daily', 1, '한글 단어 초급', '초급 한글 단어 연습 (2-3글자)'),
    ('ko-word-daily-2', 'ko', 'word', 'daily', 2, '한글 단어 중급', '중급 한글 단어 연습 (4-5글자)'),
    ('ko-word-daily-3', 'ko', 'word', 'daily', 3, '한글 단어 고급', '고급 한글 단어 연습 (6글자 이상)'),
    
    # 영어 단어 팩
    ('en-word-daily-1', 'en', 'word', 'daily', 1, 'English Words Easy', 'Easy English words (2-4 chars)'),
    ('en-word-daily-2', 'en', 'word', 'daily', 2, 'English Words Medium', 'Medium English words (5-7 chars)'),
    ('en-word-daily-3', 'en', 'word', 'daily', 3, 'English Words Hard', 'Hard English words (8-10 chars)'),
    
    # 한글 속담 팩
    ('ko-short-proverb-1', 'ko', 'short', 'proverb', 1, '한글 속담 초급', '짧은 한글 속담 (8-18자)'),
    ('ko-short-proverb-2', 'ko', 'short', 'proverb', 2, '한글 속담 중급', '중간 길이 한글 속담 (19-30자)'),
    ('ko-short-proverb-3', 'ko', 'short', 'proverb', 3, '한글 속담 고급', '긴 한글 속담 (31-60자)'),
    
    # 영어 속담 팩
    ('en-short-proverb-1', 'en', 'short', 'proverb', 1, 'English Proverbs Easy', 'Short English proverbs (15-40 chars)'),
    ('en-short-proverb-2', 'en', 'short', 'proverb', 2, 'English Proverbs Medium', 'Medium English proverbs (41-75 chars)'),
    ('en-short-proverb-3', 'en', 'short', 'proverb', 3, 'English Proverbs Hard', 'Long English proverbs (76-120 chars)'),
]


class Command(BaseCommand):
    help = 'v4.0 스펙에 맞는 12개 팩을 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write('📦 v4.0 팩 시드 시작...')
        
        created_count = 0
        exists_count = 0
        
        for code, language, kind, theme, difficulty, title, description in PACK_DEFINITIONS:
            pack, created = TextPack.objects.get_or_create(
                code=code,
                defaults={
                    'language': language,
                    'kind': kind,
                    'theme': theme,
                    'difficulty': difficulty,
                    'title': title,
                    'description': description,
                    'source': 'admin',
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ 생성: {code}')
                created_count += 1
            else:
                self.stdout.write(f'  ⏭️ 존재: {code}')
                exists_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ 완료! 생성: {created_count}개, 기존: {exists_count}개'
        ))
