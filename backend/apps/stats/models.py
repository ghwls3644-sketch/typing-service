from django.db import models
from django.conf import settings


class UserDaily(models.Model):
    """사용자 일 단위 집계 - 세션 테이블 GROUP BY 방지용"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name='사용자'
    )
    date = models.DateField(
        verbose_name='날짜',
        help_text='Asia/Seoul 기준'
    )
    language = models.CharField(
        max_length=10,
        choices=[('ko', '한글'), ('en', '영어')],
        default='ko',
        verbose_name='언어'
    )
    
    # 집계 데이터
    total_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name='세션 수'
    )
    total_duration_ms = models.BigIntegerField(
        default=0,
        verbose_name='총 연습 시간 (ms)'
    )
    avg_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='평균 WPM'
    )
    avg_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='평균 정확도 (%)'
    )
    best_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='최고 WPM'
    )
    best_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='최고 정확도 (%)'
    )
    total_chars = models.PositiveIntegerField(
        default=0,
        verbose_name='총 입력 문자수'
    )
    total_errors = models.PositiveIntegerField(
        default=0,
        verbose_name='총 오류 수'
    )
    
    # 타임스탬프
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        verbose_name = '일일 통계'
        verbose_name_plural = '일일 통계들'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date', 'language'],
                name='uq_user_date_language'
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-date'], name='idx_userdaily_user_date'),
            models.Index(fields=['-date', 'language'], name='idx_userdaily_date_lang'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.language})"
    
    @property
    def total_duration_minutes(self):
        """총 연습 시간 (분)"""
        return self.total_duration_ms / 60000


class ClientDaily(models.Model):
    """익명 사용자(guest_session_id) 일 단위 집계"""
    
    guest_session_id = models.CharField(
        max_length=100,
        verbose_name='게스트 세션 ID'
    )
    date = models.DateField(
        verbose_name='날짜',
        help_text='Asia/Seoul 기준'
    )
    language = models.CharField(
        max_length=10,
        choices=[('ko', '한글'), ('en', '영어')],
        default='ko',
        verbose_name='언어'
    )
    
    # 집계 데이터
    total_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name='세션 수'
    )
    total_duration_ms = models.BigIntegerField(
        default=0,
        verbose_name='총 연습 시간 (ms)'
    )
    sum_wpm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='WPM 합계',
        help_text='평균 계산용: avg_wpm = sum_wpm / total_sessions'
    )
    sum_accuracy = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='정확도 합계',
        help_text='평균 계산용: avg_accuracy = sum_accuracy / total_sessions'
    )
    avg_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='평균 WPM'
    )
    avg_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='평균 정확도 (%)'
    )
    best_wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='최고 WPM'
    )
    best_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='최고 정확도 (%)'
    )
    total_chars = models.PositiveIntegerField(
        default=0,
        verbose_name='총 입력 문자수'
    )
    total_errors = models.PositiveIntegerField(
        default=0,
        verbose_name='총 오류 수'
    )
    
    # 타임스탬프
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    
    class Meta:
        verbose_name = '익명 일일 통계'
        verbose_name_plural = '익명 일일 통계들'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['guest_session_id', 'date', 'language'],
                name='uq_client_date_language'
            ),
        ]
        indexes = [
            models.Index(fields=['guest_session_id', '-date'], name='idx_clientdaily_guest_date'),
            models.Index(fields=['-date', 'language'], name='idx_clientdaily_date_lang'),
        ]
    
    def __str__(self):
        return f"{self.guest_session_id[:20]} - {self.date} ({self.language})"
    
    @property
    def total_duration_minutes(self):
        """총 연습 시간 (분)"""
        return self.total_duration_ms / 60000

