from django.shortcuts import render

from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class TokenAuthenticationEx(TokenAuthentication):
    def authenticate(self, request):
        userip = get_client_ip(request)
        user_token =  super(TokenAuthenticationEx,self).authenticate(request)

        if user_token is not None:
            user, token = user_token
            if userip != user.login_ip:
                raise exceptions.AuthenticationFailed(
                    "The client's ip address has changed.\n Please sign in again."
                )
            return (user, token)
        return user_token