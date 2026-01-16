from django.contrib import admin
from .models import Badge, UserBadge, UserLevel


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category', 'rarity', 'reward_points', 'is_active', 'order']
    list_filter = ['category', 'rarity', 'is_active', 'is_secret']
    search_fields = ['name', 'code', 'description']
    ordering = ['order', 'category']
    list_editable = ['is_active', 'order']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at', 'is_featured']
    list_filter = ['badge__category', 'is_featured']
    search_fields = ['user__username', 'badge__name']
    ordering = ['-earned_at']


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'experience', 'total_points', 'updated_at']
    search_fields = ['user__username']
    ordering = ['-level', '-experience']
