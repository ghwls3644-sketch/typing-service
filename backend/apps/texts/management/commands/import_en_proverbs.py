"""
영어 속담 배치 import 커맨드
Usage: python manage.py import_en_proverbs
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import uuid


# 영어 속담 데이터
SAMPLE_EN_PROVERBS = [
    # 초급 (15-40 chars)
    "Practice makes perfect",
    "Time is money",
    "Love is blind",
    "Better late than never",
    "Actions speak louder",
    "Honesty is the best policy",
    "All that glitters is not gold",
    "Fortune favors the bold",
    "Knowledge is power",
    "Easier said than done",
    "Where there is a will",
    "No pain no gain",
    "Rome was not built in a day",
    "The early bird catches the worm",
    "A friend in need is a friend indeed",
    "Every cloud has a silver lining",
    "When in Rome do as Romans do",
    "Birds of a feather flock together",
    "Look before you leap",
    "Two wrongs do not make a right",
    
    # 중급 (41-75 chars)
    "The pen is mightier than the sword",
    "You cannot judge a book by its cover",
    "An apple a day keeps the doctor away",
    "If you want something done right do it yourself",
    "The grass is always greener on the other side",
    "A picture is worth a thousand words",
    "Do not put all your eggs in one basket",
    "You cannot make an omelette without breaking eggs",
    "If the shoe fits wear it",
    "People who live in glass houses should not throw stones",
    "When the going gets tough the tough get going",
    "You can lead a horse to water but you cannot make it drink",
    "A journey of a thousand miles begins with a single step",
    "The squeaky wheel gets the grease",
    "Absence makes the heart grow fonder",
    
    # 고급 (76-120 chars)
    "Those who do not learn from history are doomed to repeat it",
    "It is better to have loved and lost than never to have loved at all",
    "The only thing we have to fear is fear itself",
    "Give a man a fish and you feed him for a day teach him how to fish and you feed him for a lifetime",
    "The best time to plant a tree was twenty years ago the second best time is now",
    "Success is not final failure is not fatal it is the courage to continue that counts",
]


def get_difficulty(text: str) -> int:
    """속담 길이 기반 난이도 분류"""
    length = len(text)
    if length <= 40:
        return 1
    elif length <= 75:
        return 2
    else:
        return 3


class Command(BaseCommand):
    help = '영어 속담을 배치로 import합니다.'

    def handle(self, *args, **options):
        batch_id = f'import-en-proverbs-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 영어 속담 배치 import 시작... (batch_id: {batch_id})')
        
        stats = {'input': 0, 'inserted': 0, 'by_difficulty': {1: 0, 2: 0, 3: 0}}
        
        packs = {
            1: TextPack.objects.filter(code='en-short-proverb-1').first(),
            2: TextPack.objects.filter(code='en-short-proverb-2').first(),
            3: TextPack.objects.filter(code='en-short-proverb-3').first(),
        }
        
        for diff, pack in packs.items():
            if not pack:
                self.stdout.write(self.style.ERROR(f'  ❌ 팩 없음: en-short-proverb-{diff}'))
                return
        
        for proverb in SAMPLE_EN_PROVERBS:
            stats['input'] += 1
            proverb = proverb.strip()
            
            if len(proverb) < 15 or len(proverb) > 120:
                continue
            
            difficulty = get_difficulty(proverb)
            pack = packs[difficulty]
            
            normalized = TextItem.normalize_text(proverb, 'en')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=proverb,
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
