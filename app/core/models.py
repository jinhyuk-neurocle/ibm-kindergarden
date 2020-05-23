from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

class UserManager(BaseUserManager):
    """Django가 제공하는 기본 User 관리자"""
    def create_user(self, userid, password=None, **extra_fields):
        """일반 계정 생성"""
        user = self.model(userid=userid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, userid, password):
        """슈퍼 계정 생성"""
        user = self.create_user(userid, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """유저"""
    # 기본 정보
    userid = models.CharField(max_length=40, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_instructor = models.BooleanField(default=False)

    # 위치 정보, 추가 예정
    # 씨바 어캐 저장하누, 지도 API를 써봤어야 알지
    
    # 사용자 인증 관련 (Default)
    login_ip = models.CharField(null=True, max_length=255)
    verification_code =  models.CharField(null=True, max_length=16)

    objects = UserManager()
    USERNAME_FIELD = 'userid'
    
    def save(self,*args, **kwargs):
        super(User, self).save(*args, **kwargs)

