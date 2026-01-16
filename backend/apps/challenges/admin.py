from django.contrib import admin
from .models import DailyChallenge, UserChallenge


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'challenge_type', 'difficulty', 'reward_points', 'is_active']
    list_filter = ['challenge_type', 'difficulty', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-date']
    date_hierarchy = 'date'


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'status', 'current_sessions', 'reward_claimed', 'created_at']
    list_filter = ['status', 'reward_claimed']
    search_fields = ['user__username', 'challenge__title']
    ordering = ['-created_at']
