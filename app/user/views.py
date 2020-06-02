from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate

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

from core import models
from core.views import get_client_ip, TokenAuthenticationEx

class CreateUserView(generics.CreateAPIView):
    """새로운 계정 생성"""
    def post(self, request, *args, **kwargs):
        # 필수 유저 필드
        user_required_field_list = [
            'email', 'password'
        ]
        # 필수 유저 정보 필드
        user_info_required_field_list = [
            'address', 'phone',
            'parentName', 'parentGender', 'parentBirthDate', 
            'childName', 'childGender', 'childBirthDate',
            'childHeight', 'childWeight', 'childDevelopmentAge',
            # 'KDSTResult',
            'childRemark'
        ]

        try:
            # 필수 데이터 필드 중 빠진 게 없는지 검수
            required_field_list = user_required_field_list + user_info_required_field_list
            for required_field in required_field_list:
                if request.data.get(required_field) is None:
                    raise Exception(required_field)

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": {
                        "errorFrom": str(e),
                        "msg": "cannot find the value of field"
                    }
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 받은 데이터를 DB에 맞게 Parsing
            user_data, user_info_data = {}, {}
            for user_field in user_required_field_list:
                user_data[user_field] = request.data[user_field]
            for user_info_field in user_info_required_field_list:
                user_info_data[user_info_field] = request.data[user_info_field]

            # 유저 & 유저 정보 인스턴스 생성
            created_user = get_user_model().objects.create_user(**user_data)
            user_info_data['user'] = created_user
            models.UserInfo.objects.create(**user_info_data)

            return Response( { "success": True }, status=status.HTTP_200_OK )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": {
                        "errorFrom": str(e),
                        "msg": "failed to create user because of unknown reason in server"
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateTokenView(ObtainAuthToken):
    """로그인: 새로운 인증 토큰 생성"""
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if email is None or password is None:
                raise Exception("Information omission.")

            user = authenticate(request=request, username=email, password=password)
            if user is None:
                raise Exception("Incorrect e-mail address or password.")
        
        except Exception as e:
            return Response({"success": False, "msg": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_superuser:
            return Response(
                {
                    "success": False,
                    "msg": "Superuser does not need to make token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        auth_token = getattr(user, 'auth_token', None)
        if auth_token is not None:
            auth_token.delete()

        token = Token.objects.create(user=user)

        userip = get_client_ip(request)
        user.login_ip = userip
        user.save(update_fields=['login_ip'])

        return Response({"success": True, "token": token.key}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """계정 로그아웃"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

