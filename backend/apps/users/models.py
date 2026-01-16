from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    커스텀 사용자 모델
    """
    nickname = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='닉네임'
    )
    profile_image = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        verbose_name='프로필 이미지'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='가입일'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='수정일'
    )
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nickname or self.username
