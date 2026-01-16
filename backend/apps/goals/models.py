from django.db import models
from django.conf import settings


class UserGoal(models.Model):
    """사용자 일일 목표 설정"""
    
    GOAL_TYPE_CHOICES = [
        ('time', '연습 시간 (분)'),
        ('sessions', '세션 수'),
        ('chars', '입력 문자수'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ko', '한글'),
        ('en', '영어'),
        ('all', '전체'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name='사용자'
    )
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPE_CHOICES,
        default='time',
        verbose_name='목표 유형'
    )
    target_value = models.PositiveIntegerField(
        default=30,
        verbose_name='목표값',
        help_text='시간(분), 세션수, 문자수 등'
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='all',
        verbose_name='대상 언어'
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
        verbose_name = '사용자 목표'
        verbose_name_plural = '사용자 목표들'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_goal_user_active'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()}: {self.target_value}"


class UserStreak(models.Model):
    """사용자 스트릭 (연속 기록) 캐시"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
        verbose_name='사용자'
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name='현재 스트릭'
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        verbose_name='최장 스트릭'
    )
    last_active_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='마지막 활동일'
    )
    streak_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='스트릭 시작일'
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
        verbose_name = '사용자 스트릭'
        verbose_name_plural = '사용자 스트릭들'
    
    def __str__(self):
        return f"{self.user.username} - 현재 {self.current_streak}일 (최장 {self.longest_streak}일)"
    
    def update_streak(self, activity_date):
        """스트릭 업데이트 로직"""
        from datetime import timedelta
        
        if self.last_active_date is None:
            # 첫 활동
            self.current_streak = 1
            self.streak_start_date = activity_date
        elif activity_date == self.last_active_date:
            # 같은 날 중복 활동 - 스트릭 변경 없음
            pass
        elif activity_date == self.last_active_date + timedelta(days=1):
            # 연속 활동
            self.current_streak += 1
        else:
            # 스트릭 끊김 - 리셋
            self.current_streak = 1
            self.streak_start_date = activity_date
        
        # 최장 스트릭 갱신
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_active_date = activity_date
        self.save()
