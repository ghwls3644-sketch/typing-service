"""
영어 단어 배치 import 커맨드
Usage: python manage.py import_en_words
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import uuid


# 샘플 영어 단어 데이터
SAMPLE_EN_WORDS = [
    # 초급 (2-4글자)
    'go', 'be', 'do', 'is', 'am', 'it', 'to', 'me', 'we', 'an',
    'cat', 'dog', 'sun', 'run', 'big', 'red', 'hot', 'cup', 'hat', 'pen',
    'book', 'desk', 'fish', 'blue', 'cold', 'fast', 'slow', 'good', 'hand', 'home',
    'love', 'life', 'time', 'food', 'star', 'moon', 'tree', 'bird', 'rain', 'snow',
    
    # 중급 (5-7글자)
    'apple', 'water', 'music', 'happy', 'dream', 'light', 'night', 'world', 'phone', 'mouse',
    'table', 'chair', 'window', 'screen', 'laptop', 'server', 'client', 'button', 'import', 'export',
    'coding', 'typing', 'python', 'script', 'design', 'layout', 'border', 'margin', 'center', 'bottom',
    'family', 'friend', 'school', 'market', 'garden', 'coffee', 'dinner', 'forest', 'bridge', 'island',
    
    # 고급 (8-10글자)
    'computer', 'keyboard', 'software', 'hardware', 'internet', 'database', 'function', 'variable',
    'algorithm', 'component', 'framework', 'interface', 'developer', 'programmer', 'javascript',
    'beautiful', 'wonderful', 'important', 'different', 'experience', 'technology', 'university',
]


def get_difficulty(word: str) -> int:
    """단어 길이 기반 난이도 분류"""
    length = len(word)
    if length <= 4:
        return 1  # 초급
    elif length <= 7:
        return 2  # 중급
    else:
        return 3  # 고급


class Command(BaseCommand):
    help = '영어 단어를 배치로 import합니다.'

    def handle(self, *args, **options):
        batch_id = f'import-en-words-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 영어 단어 배치 import 시작... (batch_id: {batch_id})')
        
        # 통계
        stats = {'input': 0, 'inserted': 0, 'by_difficulty': {1: 0, 2: 0, 3: 0}}
        
        # 팩 가져오기
        packs = {
            1: TextPack.objects.filter(code='en-word-daily-1').first(),
            2: TextPack.objects.filter(code='en-word-daily-2').first(),
            3: TextPack.objects.filter(code='en-word-daily-3').first(),
        }
        
        for diff, pack in packs.items():
            if not pack:
                self.stdout.write(self.style.ERROR(f'  ❌ 팩 없음: en-word-daily-{diff}'))
                return
        
        # 단어 처리
        for word in SAMPLE_EN_WORDS:
            stats['input'] += 1
            word = word.strip().lower()
            
            if not word or len(word) < 2 or len(word) > 10:
                continue
            
            difficulty = get_difficulty(word)
            pack = packs[difficulty]
            
            # 중복 검사
            normalized = TextItem.normalize_text(word, 'en')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=word,
                normalized_content=normalized,
                source_name='sample_data',
                import_batch_id=batch_id,
            )
            
            stats['inserted'] += 1
            stats['by_difficulty'][difficulty] += 1
        
        self.stdout.write('\n📊 결과 통계:')
        self.stdout.write(f'  - 입력: {stats["input"]}개')
        self.stdout.write(f'  - 삽입: {stats["inserted"]}개')
        self.stdout.write(f'    - Easy(1): {stats["by_difficulty"][1]}개')
        self.stdout.write(f'    - Medium(2): {stats["by_difficulty"][2]}개')
        self.stdout.write(f'    - Hard(3): {stats["by_difficulty"][3]}개')
        self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
