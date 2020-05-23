from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

class UserSerializer(serializers.ModelSerializer):
    """계정 Object Serializer"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'userid', 'password', 'name', 'position' )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """암호화된 비밀번호로 새로운 계정 생성"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """계정 정보 업데이트"""
        password = validated_data.pop('password', None)
        user = super(UserSerializer,self).update(instance, validated_data)

        # Django: 비밀번호 변경 시 set_password 함수를 별도로 써야함
        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """계정 인증 Object Serializer"""
    userid = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """계정 인증하기"""
        userid = attrs.get('userid')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=userid,
            password=password
        )
      
        if (not user) or user.is_superuser:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs