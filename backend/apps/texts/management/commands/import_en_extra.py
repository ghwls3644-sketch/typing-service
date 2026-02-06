"""
추가 영어 단어 배치 import
Usage: python manage.py import_en_extra
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import uuid


# 추가 영어 단어 (150개)
EXTRA_EN_WORDS = [
    # 초급 (2-4글자)
    'ace', 'add', 'age', 'air', 'all', 'and', 'any', 'apt', 'arc', 'arm',
    'art', 'ask', 'ate', 'bad', 'bag', 'ban', 'bar', 'bat', 'bay', 'bed',
    'bet', 'bid', 'bit', 'box', 'boy', 'bug', 'bus', 'but', 'buy', 'can',
    'cap', 'car', 'cow', 'cry', 'cut', 'dad', 'day', 'did', 'die', 'dig',
    'dip', 'dry', 'due', 'ear', 'eat', 'egg', 'end', 'era', 'eye', 'fan',
    
    # 중급 (5-7글자)
    'about', 'above', 'actor', 'adult', 'after', 'again', 'agent', 'agree', 'ahead', 'allow',
    'alone', 'along', 'among', 'anger', 'angle', 'angry', 'apart', 'apple', 'apply', 'arena',
    'argue', 'arise', 'array', 'arrow', 'asset', 'avoid', 'award', 'aware', 'awful', 'basic',
    'beach', 'began', 'begin', 'being', 'belly', 'below', 'bench', 'bible', 'birth', 'black',
    'blade', 'blame', 'blank', 'blast', 'blend', 'blind', 'block', 'blood', 'board', 'bonus',
    
    # 고급 (8글자 이상)
    'absolute', 'abstract', 'academic', 'accepted', 'accident', 'accurate', 'achieved', 'acquired', 'activity', 'actually',
    'addition', 'adequate', 'adjusted', 'advanced', 'advocate', 'affected', 'aircraft', 'although', 'aluminum', 'analysis',
    'announce', 'anything', 'anywhere', 'apparent', 'appetite', 'approach', 'approval', 'argument', 'artistic', 'assembly',
    'assuming', 'athletic', 'attached', 'attacked', 'attempts', 'attended', 'attitude', 'attorney', 'audience', 'bachelor',
    'backward', 'bacteria', 'balanced', 'bankrupt', 'baseball', 'bathroom', 'becoming', 'behavior', 'believed', 'belonged',
]


class Command(BaseCommand):
    help = '추가 영어 단어를 import합니다.'

    def handle(self, *args, **options):
        batch_id = f'import-en-extra-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 추가 영어 단어 import 시작... (batch_id: {batch_id})')
        
        packs = {
            1: TextPack.objects.filter(code='en-word-daily-1').first(),
            2: TextPack.objects.filter(code='en-word-daily-2').first(),
            3: TextPack.objects.filter(code='en-word-daily-3').first(),
        }
        
        stats = {1: 0, 2: 0, 3: 0}
        
        for word in EXTRA_EN_WORDS:
            word = word.strip().lower()
            length = len(word)
            
            if length <= 4:
                difficulty = 1
            elif length <= 7:
                difficulty = 2
            else:
                difficulty = 3
            
            pack = packs.get(difficulty)
            if not pack:
                continue
            
            normalized = TextItem.normalize_text(word, 'en')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=word,
                normalized_content=normalized,
                source_name='extra_data',
                import_batch_id=batch_id,
            )
            stats[difficulty] += 1
        
        self.stdout.write('\n📊 결과 통계:')
        self.stdout.write(f'  - Easy: {stats[1]}개')
        self.stdout.write(f'  - Medium: {stats[2]}개')
        self.stdout.write(f'  - Hard: {stats[3]}개')
        self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
