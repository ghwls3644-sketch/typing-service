from django.db import models
from django.conf import settings


class Snapshot(models.Model):
    """랭킹 스냅샷 - 주기별 랭킹 집계"""
    
    PERIOD_CHOICES = [
        ('daily', '일간'),
        ('weekly', '주간'),
        ('monthly', '월간'),
    ]
    
    MODE_CHOICES = [
        ('practice', '연습'),
        ('ranked', '랭킹전'),
        ('all', '전체'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ko', '한글'),
        ('en', '영어'),
        ('all', '전체'),
    ]
    
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default='weekly',
        verbose_name='기간',
        db_index=True
    )
    start_date = models.DateField(
        verbose_name='기간 시작',
        db_index=True
    )
    end_date = models.DateField(
        verbose_name='기간 끝'
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='all',
        verbose_name='모드',
        db_index=True
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='all',
        verbose_name='언어',
        db_index=True
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성 시각'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화'
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
        verbose_name = '랭킹 스냅샷'
        verbose_name_plural = '랭킹 스냅샷들'
        ordering = ['-generated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['period', 'start_date', 'end_date', 'mode', 'language'],
                name='uq_snapshot_period'
            ),
        ]
        indexes = [
            models.Index(fields=['period', '-start_date'], name='idx_snapshot_period_start'),
            models.Index(fields=['language', 'period', '-start_date'], name='idx_snapshot_lang_period'),
        ]
    
    def __str__(self):
        return f"{self.get_period_display()} {self.start_date} ~ {self.end_date} ({self.language})"
    
    @property
    def entry_count(self):
        return self.entries.count()


class Entry(models.Model):
    """랭킹 엔트리 - 스냅샷 내 개별 순위"""
    
    snapshot = models.ForeignKey(
        Snapshot,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='스냅샷',
        db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        verbose_name='사용자',
        db_index=True
    )
    rank = models.PositiveIntegerField(
        verbose_name='순위',
        db_index=True
    )
    score_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='평균 WPM'
    )
    score_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='평균 정확도 (%)'
    )
    session_count = models.PositiveIntegerField(
        default=0,
        verbose_name='세션 수'
    )
    best_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='최고 WPM'
    )
    total_duration_ms = models.BigIntegerField(
        default=0,
        verbose_name='총 연습 시간 (ms)'
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
        verbose_name = '랭킹 엔트리'
        verbose_name_plural = '랭킹 엔트리들'
        ordering = ['rank']
        constraints = [
            models.UniqueConstraint(
                fields=['snapshot', 'user'],
                name='uq_entry_snapshot_user'
            ),
            models.UniqueConstraint(
                fields=['snapshot', 'rank'],
                name='uq_entry_snapshot_rank'
            ),
        ]
        indexes = [
            models.Index(fields=['snapshot', 'rank'], name='idx_entry_snapshot_rank'),
            models.Index(fields=['user', '-created_at'], name='idx_entry_user_created'),
        ]
    
    def __str__(self):
        return f"#{self.rank} {self.user.username} - {self.score_wpm}WPM"
