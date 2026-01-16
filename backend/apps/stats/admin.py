from django.contrib import admin
from .models import UserDaily


@admin.register(UserDaily)
class UserDailyAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'language', 'total_sessions', 'avg_wpm', 'avg_accuracy', 'best_wpm']
    list_filter = ['language', 'date']
    search_fields = ['user__username']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
