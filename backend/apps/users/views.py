from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserEmailChangeSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """회원가입 API"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer


class ProfileView(APIView):
    """프로필 조회/수정 API (username/email은 read_only)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangeEmailView(APIView):
    """이메일 변경 API (비밀번호 확인 필요)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserEmailChangeSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.email = serializer.validated_data['new_email']
        request.user.save(update_fields=['email'])
        return Response({'detail': '이메일이 변경되었습니다.'}, status=status.HTTP_200_OK)
