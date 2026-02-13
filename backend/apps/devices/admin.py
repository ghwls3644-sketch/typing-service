from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('guest_session_id', 'nickname', 'created_at', 'last_seen_at')
    search_fields = ('guest_session_id', 'nickname')
    readonly_fields = ('created_at', 'last_seen_at')
    list_filter = ('created_at',)
