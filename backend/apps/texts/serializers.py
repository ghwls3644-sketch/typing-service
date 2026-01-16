from rest_framework import serializers
from .models import TextPack, TextItem


class TextItemSerializer(serializers.ModelSerializer):
    """문장 상세 직렬화"""
    
    class Meta:
        model = TextItem
        fields = [
            'id', 'pack', 'content', 'length', 'punctuation_level',
            'is_active', 'order', 'word_count', 'char_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TextItemListSerializer(serializers.ModelSerializer):
    """문장 목록 직렬화"""
    
    class Meta:
        model = TextItem
        fields = ['id', 'content', 'length', 'order']


class TextPackSerializer(serializers.ModelSerializer):
    """문장팩 상세 직렬화"""
    item_count = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = TextPack
        fields = [
            'id', 'title', 'language', 'language_display', 'difficulty',
            'source', 'description', 'is_active', 'item_count',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TextPackListSerializer(serializers.ModelSerializer):
    """문장팩 목록 직렬화"""
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TextPack
        fields = ['id', 'title', 'language', 'difficulty', 'item_count']


class TextPackDetailSerializer(serializers.ModelSerializer):
    """문장팩 상세 (문장 포함) 직렬화"""
    items = TextItemListSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TextPack
        fields = [
            'id', 'title', 'language', 'difficulty', 'source', 'description',
            'is_active', 'item_count', 'items', 'created_at'
        ]
