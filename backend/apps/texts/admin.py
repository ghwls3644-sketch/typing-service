from django.contrib import admin
from .models import TextPack, TextItem


@admin.register(TextPack)
class TextPackAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'language', 'difficulty', 'item_count', 'is_active', 'created_at']
    list_filter = ['language', 'difficulty', 'is_active', 'source']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    def item_count(self, obj):
        return obj.items.filter(is_active=True).count()
    item_count.short_description = '문장 수'


@admin.register(TextItem)
class TextItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_content', 'pack', 'length', 'punctuation_level', 'is_active', 'order']
    list_filter = ['pack', 'is_active', 'pack__language']
    search_fields = ['content']
    list_editable = ['is_active', 'order']
    ordering = ['pack', 'order', '-created_at']
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '문장 내용'
