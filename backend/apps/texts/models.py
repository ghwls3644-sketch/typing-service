from django.db import models
from django.conf import settings
import unicodedata
import re


class TextPack(models.Model):
    """문장팩 모델 - 문장 그룹"""
    
    LANGUAGE_CHOICES = [
        ('ko', '한글'),
        ('en', '영어'),
    ]
    
    KIND_CHOICES = [
        ('word', '단어'),
        ('short', '짧은글'),
    ]
    
    THEME_CHOICES = [
        ('daily', '일반'),
        ('proverb', '속담'),
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
    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        default='word',
        verbose_name='유형',
        db_index=True
    )
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='daily',
        verbose_name='테마',
        db_index=True
    )
    difficulty = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='난이도 (1-3)',
        help_text='1: 초급, 2: 중급, 3: 고급',
        db_index=True
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name='팩 코드',
        help_text='예: ko-word-daily-1'
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
        ordering = ['language', 'kind', 'difficulty', '-created_at']
        indexes = [
            models.Index(fields=['language', 'is_active', 'difficulty'], name='idx_pack_lang_active_diff'),
            models.Index(fields=['language', 'kind', 'theme', 'difficulty', 'is_active'], name='idx_pack_practice'),
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
    normalized_content = models.TextField(
        blank=True,
        verbose_name='정규화된 내용',
        help_text='중복 검사용 정규화된 텍스트'
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
    # 출처 추적 필드
    source_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='출처명'
    )
    import_batch_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='배치 ID',
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
            models.Index(fields=['import_batch_id'], name='idx_item_batch'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['pack', 'normalized_content'],
                name='unique_pack_normalized_content'
            )
        ]
    
    def __str__(self):
        return f"{self.content[:50]}..." if len(self.content) > 50 else self.content
    
    @staticmethod
    def normalize_text(text: str, language: str = 'ko') -> str:
        """텍스트 정규화 함수"""
        # 1. 앞뒤 공백 제거
        text = text.strip()
        # 2. 내부 연속 공백 1개로 축약
        text = re.sub(r'\s+', ' ', text)
        # 3. 제로폭/제어문자 제거
        text = ''.join(c for c in text if unicodedata.category(c) not in ('Cc', 'Cf') or c == ' ')
        # 4. KO NFC 정규화
        if language == 'ko':
            text = unicodedata.normalize('NFC', text)
        # 5. 끝 문장부호 제거
        text = re.sub(r'[.!?]+$', '', text)
        # 6. EN은 소문자화 (중복 판정용)
        if language == 'en':
            text = text.lower()
        return text
    
    def save(self, *args, **kwargs):
        # 자동으로 글자 수 계산
        if not self.length:
            self.length = len(self.content.replace(' ', ''))
        # 정규화된 콘텐츠 생성
        if not self.normalized_content and self.content:
            lang = self.pack.language if self.pack else 'ko'
            self.normalized_content = self.normalize_text(self.content, lang)
        super().save(*args, **kwargs)
    
    @property
    def word_count(self):
        """단어 수 계산"""
        return len(self.content.split())
    
    @property
    def char_count(self):
        """문자 수 계산"""
        return len(self.content)
