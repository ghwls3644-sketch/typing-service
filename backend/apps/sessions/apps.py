from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sessions'
    label = 'typing_sessions'  # django.contrib.sessions와 충돌 방지
    verbose_name = '타자 세션'

