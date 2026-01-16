from django.contrib import admin
from .models import UserGoal, UserStreak


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_type', 'target_value', 'language', 'is_active']
    list_filter = ['goal_type', 'language', 'is_active']
    search_fields = ['user__username']
    ordering = ['-created_at']


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_active_date']
    search_fields = ['user__username']
    ordering = ['-current_streak']
