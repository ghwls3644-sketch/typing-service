"""
단어 데이터 통합 시드 커맨드
Usage: 
  python manage.py seed_words          # 전체 시드
  python manage.py seed_words --lang ko # 한국어만
  python manage.py seed_words --lang en # 영어만
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
from apps.texts.data.words_ko import KO_WORDS, KO_PROVERBS
from apps.texts.data.words_en import EN_WORDS
import uuid

class Command(BaseCommand):
    help = '연습용 단어 및 속담 데이터를 DB에 적재합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lang',
            type=str,
            choices=['ko', 'en'],
            help='특정 언어만 시드 (생략 시 전체)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='DB 저장 없이 시뮬레이션'
        )

    def handle(self, *args, **options):
        batch_id = f'seed-words-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'🌱 단어 데이터 시딩 시작... (batch_id: {batch_id})')
        
        target_lang = options['lang']
        dry_run = options['dry_run']

        # 1. 한국어 처리
        if not target_lang or target_lang == 'ko':
            self.stdout.write('\n[한국어 단어 처리]')
            self.process_items(KO_WORDS, 'ko', 'word', {
                1: (2, 3),
                2: (4, 6),
                3: (7, 12)
            }, batch_id, dry_run)
            
            self.stdout.write('\n[한국어 속담 처리]')
            self.process_items(KO_PROVERBS, 'ko', 'short', {
                1: (0, 18),
                2: (19, 30),
                3: (31, 999)
            }, batch_id, dry_run)

        # 2. 영어 처리
        if not target_lang or target_lang == 'en':
            self.stdout.write('\n[영어 단어 처리]')
            self.process_items(EN_WORDS, 'en', 'word', {
                1: (2, 4),
                2: (5, 7),
                3: (8, 999)
            }, batch_id, dry_run)

        self.stdout.write(self.style.SUCCESS(f'\n✅ 모든 작업 완료!'))

    def process_items(self, items, lang, mode, criteria, batch_id, dry_run):
        count = 0
        skipped = 0
        newly_added = 0
        
        # 팩 캐싱
        packs = {}
        # mode가 'word'면 daily, 'short'면 proverb (현재 구조상)
        theme = 'daily' if mode == 'word' else 'proverb'
        
        for diff in [1, 2, 3]:
            # 코드 포맷: {lang}-{mode}-{theme}-{diff}
            # 예: ko-word-daily-1, ko-short-proverb-1
            # 확인이 필요함. import_ko_extra.py에서 proverb는 ko-short-proverb-X 였음.
            code = f'{lang}-{mode}-{theme}-{diff}'
            packs[diff] = TextPack.objects.filter(code=code).first()
            if not packs[diff]:
                self.stdout.write(self.style.ERROR(f'❌ 팩을 찾을 수 없음: {code}'))
        
        for content in items:
            content = content.strip()
            if not content:
                continue
                
            length = len(content)
            
            # 난이도 결정
            difficulty = 0
            for d, (min_len, max_len) in criteria.items():
                if min_len <= length <= max_len:
                    difficulty = d
                    break
            
            if difficulty == 0:
                # 범위 밖이면 가장 가까운 난이도 혹은 스킵
                # 간단히 스킵
                skipped += 1
                continue
            
            pack = packs.get(difficulty)
            if not pack:
                skipped += 1
                continue
                
            # 중복 검사
            normalized = TextItem.normalize_text(content, lang)
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                skipped += 1
                continue
            
            # 저장
            if not dry_run:
                TextItem.objects.create(
                    pack=pack,
                    content=content,
                    normalized_content=normalized,
                    source_name='seed_script',
                    import_batch_id=batch_id
                )
            newly_added += 1
            count += 1
            
        self.stdout.write(f'  - 처리: {len(items)}, 신규: {newly_added}, 스킵(중복/범위초과): {skipped}')
