from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 직렬화 (프로필 수정 시 민감 필드 보호)"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'created_at']
        read_only_fields = ['id', 'username', 'email', 'created_at']


class UserEmailChangeSerializer(serializers.Serializer):
    """이메일 변경 시 비밀번호 확인 필요"""
    current_password = serializers.CharField(write_only=True)
    new_email = serializers.EmailField()

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')
        return value

    def validate_new_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.context['request'].user.pk).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """회원가입 직렬화"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'nickname']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
