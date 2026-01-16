from django.db import models
from django.conf import settings


class TextPack(models.Model):
    """문장팩 모델 - 문장 그룹"""
    
    LANGUAGE_CHOICES = [
        ('ko', '한글'),
        ('en', '영어'),
    ]
    
    SOURCE_CHOICES = [
        ('admin', '관리자'),
        ('user', '사용자'),
        ('import', '가져오기'),
    ]
    
    title = models.CharField(
        max_length=100,
        verbose_name='문장팩 이름',
        db_index=True
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='ko',
        verbose_name='언어',
        db_index=True
    )
    difficulty = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='난이도 (1-5)',
        help_text='1: 매우 쉬움, 5: 매우 어려움',
        db_index=True
    )
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default='admin',
        blank=True,
        verbose_name='출처'
    )
    description = models.TextField(
        blank=True,
        verbose_name='설명'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='노출 여부',
        db_index=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_packs',
        verbose_name='생성자',
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        verbose_name = '문장팩'
        verbose_name_plural = '문장팩들'
        ordering = ['language', 'difficulty', '-created_at']
        indexes = [
            models.Index(fields=['language', 'is_active', 'difficulty'], name='idx_pack_lang_active_diff'),
        ]
    
    def __str__(self):
        return f"[{self.get_language_display()}] {self.title}"
    
    @property
    def item_count(self):
        return self.items.filter(is_active=True).count()


class TextItem(models.Model):
    """연습용 문장 모델"""
    
    pack = models.ForeignKey(
        TextPack,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='소속 문장팩',
        db_index=True
    )
    content = models.TextField(
        verbose_name='문장 내용'
    )
    length = models.PositiveIntegerField(
        default=0,
        verbose_name='글자 수',
        help_text='난이도/추천/통계용',
        db_index=True
    )
    punctuation_level = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='기호 난이도',
        help_text='특수문자/기호 포함 정도 (0-5)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화',
        db_index=True
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='팩 내 순서',
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        verbose_name = '연습 문장'
        verbose_name_plural = '연습 문장들'
        ordering = ['pack', 'order', '-created_at']
        indexes = [
            models.Index(fields=['pack', 'is_active'], name='idx_item_pack_active'),
            models.Index(fields=['pack', 'order'], name='idx_item_pack_order'),
        ]
    
    def __str__(self):
        return f"{self.content[:50]}..." if len(self.content) > 50 else self.content
    
    def save(self, *args, **kwargs):
        # 자동으로 글자 수 계산
        if not self.length:
            self.length = len(self.content.replace(' ', ''))
        super().save(*args, **kwargs)
    
    @property
    def word_count(self):
        """단어 수 계산"""
        return len(self.content.split())
    
    @property
    def char_count(self):
        """문자 수 계산"""
        return len(self.content)
