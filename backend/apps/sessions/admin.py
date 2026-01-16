from django.contrib import admin
from .models import TypingSession, TypingEvent


@admin.register(TypingSession)
class TypingSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mode', 'language', 'wpm', 'accuracy', 'duration_ms', 'started_at']
    list_filter = ['mode', 'language', 'started_at']
    search_fields = ['user__username', 'text_content', 'guest_session_id']
    ordering = ['-started_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user', 'guest_session_id')
        }),
        ('연습 정보', {
            'fields': ('pack', 'text_item', 'text_content', 'mode', 'language')
        }),
        ('시간', {
            'fields': ('started_at', 'ended_at', 'duration_ms')
        }),
        ('결과', {
            'fields': ('input_length', 'correct_length', 'error_count', 'accuracy', 'wpm', 'cpm')
        }),
        ('확장', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(TypingEvent)
class TypingEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 't_ms', 'expected', 'typed', 'is_correct', 'position']
    list_filter = ['is_correct']
    search_fields = ['session__id']
    ordering = ['session', 't_ms']
