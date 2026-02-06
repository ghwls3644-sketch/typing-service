"""
마이그레이션: UniqueConstraint 추가 (데이터 정규화 완료 후)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '0004_migrate_difficulty_deactivate_legacy'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='textitem',
            constraint=models.UniqueConstraint(
                fields=('pack', 'normalized_content'), 
                name='unique_pack_normalized_content'
            ),
        ),
    ]
