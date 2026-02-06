"""
데이터 마이그레이션: 
1. 기존 TextItem의 normalized_content 채우기
2. 난이도 1~5 → 1~3 변환 
3. 기존 팩 비활성화
"""
from django.db import migrations
import unicodedata
import re


def normalize_text(text: str, language: str = 'ko') -> str:
    """텍스트 정규화 함수"""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = ''.join(c for c in text if unicodedata.category(c) not in ('Cc', 'Cf') or c == ' ')
    if language == 'ko':
        text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[.!?]+$', '', text)
    if language == 'en':
        text = text.lower()
    return text


def migrate_data(apps, schema_editor):
    """데이터 마이그레이션"""
    TextPack = apps.get_model('texts', 'TextPack')
    TextItem = apps.get_model('texts', 'TextItem')
    
    # 1. TextItem normalized_content 채우기
    items = TextItem.objects.select_related('pack').all()
    for item in items:
        lang = item.pack.language if item.pack else 'ko'
        item.normalized_content = normalize_text(item.content, lang)
        item.save(update_fields=['normalized_content'])
    print(f"  - normalized_content 채움: {items.count()}개 아이템")
    
    # 2. 난이도 변환: 1-2 -> 1, 3 -> 2, 4-5 -> 3
    TextPack.objects.filter(difficulty__in=[1, 2]).update(difficulty=1)
    TextPack.objects.filter(difficulty=3).update(difficulty=2)
    TextPack.objects.filter(difficulty__in=[4, 5]).update(difficulty=3)
    print(f"  - 난이도 변환 완료")
    
    # 3. 기존 팩 비활성화 (code가 없는 레거시 팩)
    legacy_count = TextPack.objects.filter(code__isnull=True).update(is_active=False)
    print(f"  - 레거시 팩 비활성화: {legacy_count}개")


def reverse_migration(apps, schema_editor):
    """역마이그레이션"""
    TextPack = apps.get_model('texts', 'TextPack')
    TextPack.objects.filter(code__isnull=True).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '0003_add_v4_fields'),
    ]

    operations = [
        migrations.RunPython(
            migrate_data,
            reverse_code=reverse_migration
        ),
    ]
