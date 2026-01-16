from django.contrib import admin
from .models import Snapshot, Entry


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ['id', 'period', 'start_date', 'end_date', 'mode', 'language', 'entry_count', 'generated_at']
    list_filter = ['period', 'mode', 'language', 'is_active']
    ordering = ['-generated_at']
    date_hierarchy = 'start_date'


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['snapshot', 'rank', 'user', 'score_wpm', 'score_accuracy', 'session_count']
    list_filter = ['snapshot__period', 'snapshot__language']
    search_fields = ['user__username']
    ordering = ['snapshot', 'rank']
