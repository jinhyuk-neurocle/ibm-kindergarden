from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework import generics, viewsets, mixins, status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from core.views import get_client_ip, TokenAuthenticationEx
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """새로운 계정 생성"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """새로운 인증 토큰 생성"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_superuser:
            return Response(
                {"message": "superuser does not need to make token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        auth_token = getattr(user, 'auth_token', None)
        if auth_token is not None:
            auth_token.delete()

        token = Token.objects.create(user=user)

        userip = get_client_ip(request)
        user.login_ip = userip
        user.save(update_fields=['login_ip'])

        return Response({
            'token': token.key,
            'userid': user.userid,
            'user_db_id': user.id,
        })

class LogoutView(APIView):
    """계정 로그아웃"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

