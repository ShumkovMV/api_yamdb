from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.validators import ValidationError

from users.models import CustomUser


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name',
        )


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name',
        )
        read_only_fields = ('role',)


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UnicodeUsernameValidator(),
        ],
        max_length=128,
    )
    email = serializers.EmailField(max_length=150)

    def create(self, validated_data):
        try:
            user, _ = CustomUser.objects.get_or_create(**validated_data)
        except IntegrityError:
            raise ValidationError('Имя пользователя или email не валидно')
        return user

    class Meta:
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
