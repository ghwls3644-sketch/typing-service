from django.db import models
from django.conf import settings


class Badge(models.Model):
    """뱃지 정의"""
    
    CATEGORY_CHOICES = [
        ('speed', '속도'),
        ('accuracy', '정확도'),
        ('streak', '연속일'),
        ('challenge', '챌린지'),
        ('milestone', '마일스톤'),
        ('special', '특별'),
    ]
    
    RARITY_CHOICES = [
        (1, '일반'),
        (2, '희귀'),
        (3, '영웅'),
        (4, '전설'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='코드',
        help_text='시스템에서 사용하는 고유 코드'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='뱃지 이름'
    )
    description = models.TextField(
        blank=True,
        verbose_name='설명'
    )
    icon = models.CharField(
        max_length=50,
        default='🏆',
        verbose_name='아이콘'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='milestone',
        verbose_name='카테고리'
    )
    rarity = models.PositiveSmallIntegerField(
        choices=RARITY_CHOICES,
        default=1,
        verbose_name='희귀도'
    )
    
    # 획득 조건
    condition_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='조건 유형',
        help_text='wpm_reach, accuracy_reach, streak_reach, sessions_complete 등'
    )
    condition_value = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='조건 값'
    )
    
    # 보상
    reward_points = models.PositiveIntegerField(
        default=50,
        verbose_name='보상 포인트'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화'
    )
    is_secret = models.BooleanField(
        default=False,
        verbose_name='시크릿 뱃지',
        help_text='획득 전까지 숨김'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='정렬 순서'
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
        verbose_name = '뱃지'
        verbose_name_plural = '뱃지들'
        ordering = ['order', 'category', 'rarity']
        indexes = [
            models.Index(fields=['category', 'is_active'], name='idx_badge_category'),
            models.Index(fields=['condition_type'], name='idx_badge_condition'),
        ]
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """사용자 뱃지 획득 기록"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
        verbose_name='사용자'
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='owners',
        verbose_name='뱃지'
    )
    earned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='획득 시각'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='대표 뱃지',
        help_text='프로필에 표시할 대표 뱃지'
    )
    
    class Meta:
        verbose_name = '사용자 뱃지'
        verbose_name_plural = '사용자 뱃지들'
        ordering = ['-earned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'badge'],
                name='uq_user_badge'
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-earned_at'], name='idx_ub_user_earned'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserLevel(models.Model):
    """사용자 레벨 정보"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='level',
        verbose_name='사용자'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='레벨'
    )
    experience = models.PositiveIntegerField(
        default=0,
        verbose_name='경험치'
    )
    total_points = models.PositiveIntegerField(
        default=0,
        verbose_name='총 포인트'
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
        verbose_name = '사용자 레벨'
        verbose_name_plural = '사용자 레벨들'
    
    def __str__(self):
        return f"{self.user.username} - Lv.{self.level}"
    
    @property
    def exp_to_next_level(self):
        """다음 레벨까지 필요한 경험치"""
        return self.level * 100  # 레벨 * 100
    
    @property
    def progress_percent(self):
        """레벨 진행률"""
        return min((self.experience / self.exp_to_next_level) * 100, 100)
    
    def add_experience(self, exp):
        """경험치 추가 및 레벨업 체크"""
        self.experience += exp
        while self.experience >= self.exp_to_next_level:
            self.experience -= self.exp_to_next_level
            self.level += 1
        self.save()
    
    def add_points(self, points):
        """포인트 추가"""
        self.total_points += points
        self.save()
