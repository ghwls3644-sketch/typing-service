from django.db import models
from django.conf import settings


class DailyChallenge(models.Model):
    """데일리 챌린지 - 매일 새로운 도전"""
    
    CHALLENGE_TYPE_CHOICES = [
        ('speed', '속도 챌린지'),
        ('accuracy', '정확도 챌린지'),
        ('endurance', '지구력 챌린지'),
        ('special', '특별 챌린지'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, '쉬움'),
        (2, '보통'),
        (3, '어려움'),
        (4, '극한'),
    ]
    
    date = models.DateField(
        unique=True,
        verbose_name='챌린지 날짜'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='챌린지 제목'
    )
    description = models.TextField(
        verbose_name='챌린지 설명'
    )
    challenge_type = models.CharField(
        max_length=20,
        choices=CHALLENGE_TYPE_CHOICES,
        default='speed',
        verbose_name='챌린지 유형'
    )
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES,
        default=2,
        verbose_name='난이도'
    )
    
    # 목표
    target_wpm = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='목표 WPM'
    )
    target_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='목표 정확도 (%)'
    )
    target_sessions = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='목표 세션 수'
    )
    target_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='목표 시간 (분)'
    )
    
    # 지정 텍스트 (선택)
    text_pack = models.ForeignKey(
        'texts.TextPack',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='지정 문장팩'
    )
    
    # 보상
    reward_points = models.PositiveIntegerField(
        default=100,
        verbose_name='보상 포인트'
    )
    reward_badge = models.ForeignKey(
        'achievements.Badge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='challenges',
        verbose_name='보상 뱃지'
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
        verbose_name = '데일리 챌린지'
        verbose_name_plural = '데일리 챌린지들'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date', 'is_active'], name='idx_challenge_date_active'),
        ]
    
    def __str__(self):
        return f"[{self.date}] {self.title}"


class UserChallenge(models.Model):
    """사용자 챌린지 참가 기록"""
    
    STATUS_CHOICES = [
        ('in_progress', '진행 중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenges',
        verbose_name='사용자'
    )
    challenge = models.ForeignKey(
        DailyChallenge,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='챌린지'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='상태'
    )
    
    # 진행 상황
    current_wpm = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='현재 WPM'
    )
    current_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='현재 정확도 (%)'
    )
    current_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name='현재 세션 수'
    )
    current_time_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name='현재 시간 (분)'
    )
    
    # 보상
    reward_claimed = models.BooleanField(
        default=False,
        verbose_name='보상 수령 여부'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='시작 시각'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='완료 시각'
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
        verbose_name = '사용자 챌린지'
        verbose_name_plural = '사용자 챌린지들'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'challenge'],
                name='uq_user_challenge'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_uc_user_status'),
            models.Index(fields=['challenge', 'status'], name='idx_uc_challenge_status'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.get_status_display()})"
    
    def check_completion(self):
        """챌린지 완료 여부 확인"""
        from django.utils import timezone
        
        challenge = self.challenge
        completed = True
        
        if challenge.target_wpm and (not self.current_wpm or self.current_wpm < challenge.target_wpm):
            completed = False
        if challenge.target_accuracy and (not self.current_accuracy or self.current_accuracy < challenge.target_accuracy):
            completed = False
        if challenge.target_sessions and self.current_sessions < challenge.target_sessions:
            completed = False
        if challenge.target_time_minutes and self.current_time_minutes < challenge.target_time_minutes:
            completed = False
        
        if completed and self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
        
        return completed
