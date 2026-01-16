from django.db import models
from django.conf import settings


class TypingSession(models.Model):
    """타자 연습 세션 모델 - 원천 데이터"""
    
    MODE_CHOICES = [
        ('practice', '연습'),
        ('challenge', '챌린지'),
        ('ranked', '랭킹전'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ko', '한글'),
        ('en', '영어'),
    ]
    
    # 사용자/연결 정보
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='typing_sessions',
        null=True,
        blank=True,
        verbose_name='사용자',
        db_index=True
    )
    pack = models.ForeignKey(
        'texts.TextPack',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions',
        verbose_name='문장팩',
        db_index=True
    )
    text_item = models.ForeignKey(
        'texts.TextItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions',
        verbose_name='연습 문장',
        db_index=True
    )
    
    # 세션 메타
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='practice',
        verbose_name='모드',
        db_index=True
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='ko',
        verbose_name='언어',
        db_index=True
    )
    text_content = models.TextField(
        verbose_name='연습한 문장 내용',
        help_text='원본 문장 삭제 시에도 기록 유지를 위해 저장'
    )
    
    # 시간 정보
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='시작 시각',
        db_index=True
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='종료 시각'
    )
    duration_ms = models.PositiveIntegerField(
        default=0,
        verbose_name='소요 시간 (ms)'
    )
    
    # 입력/결과 정보
    input_length = models.PositiveIntegerField(
        default=0,
        verbose_name='총 입력 길이'
    )
    correct_length = models.PositiveIntegerField(
        default=0,
        verbose_name='정확 입력 길이'
    )
    error_count = models.PositiveIntegerField(
        default=0,
        verbose_name='오타 수'
    )
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='정확도 (%)',
        db_index=True
    )
    wpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='WPM (분당 단어수)',
        db_index=True
    )
    cpm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='CPM (분당 문자수)'
    )
    
    # 확장 필드
    metadata = models.JSONField(
        null=True,
        blank=True,
        verbose_name='메타데이터',
        help_text='기기/브라우저/키보드 등 확장 정보'
    )
    guest_session_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='게스트 세션 ID',
        help_text='비로그인 사용자 식별용'
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
        verbose_name = '타자 세션'
        verbose_name_plural = '타자 세션들'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at'], name='idx_session_user_started'),
            models.Index(fields=['mode', 'language', '-started_at'], name='idx_session_mode_lang'),
            models.Index(fields=['pack', '-started_at'], name='idx_session_pack_started'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(accuracy__gte=0) & models.Q(accuracy__lte=100),
                name='chk_accuracy_range'
            ),
            models.CheckConstraint(
                check=models.Q(wpm__gte=0),
                name='chk_wpm_positive'
            ),
            models.CheckConstraint(
                check=models.Q(error_count__gte=0),
                name='chk_error_positive'
            ),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else f'Guest'
        return f"{user_str} - {self.wpm}WPM / {self.accuracy}% ({self.started_at.strftime('%Y-%m-%d %H:%M')})"


class TypingEvent(models.Model):
    """키 입력/오타 이벤트 로그 (선택적 기능, 기본 비활성)"""
    
    session = models.ForeignKey(
        TypingSession,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='세션',
        db_index=True
    )
    t_ms = models.PositiveIntegerField(
        verbose_name='시간 오프셋 (ms)',
        help_text='세션 시작 기준 밀리초'
    )
    expected = models.CharField(
        max_length=5,
        blank=True,
        verbose_name='기대 문자'
    )
    typed = models.CharField(
        max_length=5,
        blank=True,
        verbose_name='입력 문자'
    )
    is_correct = models.BooleanField(
        default=True,
        verbose_name='정오타',
        db_index=True
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='문장 내 위치'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    
    class Meta:
        verbose_name = '타이핑 이벤트'
        verbose_name_plural = '타이핑 이벤트들'
        ordering = ['session', 't_ms']
        indexes = [
            models.Index(fields=['session', 't_ms'], name='idx_event_session_t'),
            models.Index(fields=['session', 'is_correct'], name='idx_event_session_correct'),
        ]
    
    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f"{status} [{self.expected}] -> [{self.typed}] at {self.t_ms}ms"
