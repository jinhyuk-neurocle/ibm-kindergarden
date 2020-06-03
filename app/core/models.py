from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

class UserManager(BaseUserManager):
    """Django가 제공하는 기본 User 관리자"""
    def create_user(self, email, password=None, **extra_fields):
        """일반 계정 생성"""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password):
        """슈퍼 계정 생성"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """유저"""
    email = models.EmailField(max_length=255, unique=True)
    description = models.CharField(max_length=2048, null=True)

    # 사용자 인증 관련 (Default)
    is_superuser = models.BooleanField(default=False)
    login_ip = models.CharField(null=True, max_length=255)
    verification_code = models.CharField(null=True, max_length=16)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    
    def save(self,*args, **kwargs):
        super(User, self).save(*args, **kwargs)


class UserInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    address = models.CharField(max_length=1024)
    parentName = models.CharField(max_length=32)
    parentBirthDate = models.DateField()
    parentGender = models.CharField(max_length=8)
    phone = models.CharField(max_length=32)

    childName = models.CharField(max_length=32)
    childGender = models.CharField(max_length=8)
    childBirthDate = models.DateField()
    childHeight = models.FloatField()
    childWeight = models.FloatField()
    childDevelopmentAge = models.IntegerField()
    #KDSTResult = models...
    childRemark = models.CharField(max_length=2048)
    
    # 등록된 주소의 위도/경도
    addressX = models.FloatField(default=0.0)
    addressY = models.FloatField(default=0.0)

class InstructorInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    parentName = models.CharField(max_length=32)
    parentBirthDate = models.DateField()
    parentGender = models.CharField(max_length=8)
    phone = models.CharField(max_length=32)

class MeetingGroup(models.Model):
    """성사된 모임"""
    member = models.ManyToManyField(settings.AUTH_USER_MODEL)

    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    meeting_date = models.DateTimeField()
    is_closed = models.BooleanField(default=False)

class MeetingReview(models.Model):
    """모임의 리뷰"""
    meeting_group = models.ForeignKey(MeetingGroup, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=512)


class Cluster(models.Model):
    """주변인을 찾기 위한 클러스터"""
    # 추후 수정
    pass

