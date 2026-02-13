from django.db import models


class Client(models.Model):
    """
    익명 사용자 프로필.
    guest_session_id를 PK로 사용하여 로그인 없이 사용자를 식별합니다.
    """
    guest_session_id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text='프론트엔드에서 생성한 익명 식별자 (guest_{timestamp}_{random})',
    )
    nickname = models.CharField(
        max_length=24,
        null=True,
        blank=True,
        help_text='표시 이름 (기본: 익명-XXXX)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    ua_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='User-Agent 해시 (선택)',
    )
    meta = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text='추가 메타 정보',
    )

    class Meta:
        db_table = 'devices_client'
        verbose_name = '클라이언트'
        verbose_name_plural = '클라이언트'

    def __str__(self):
        return self.nickname or f'익명-{self.guest_session_id[:8]}'

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = f'익명-{self.guest_session_id[-4:]}'
        super().save(*args, **kwargs)
