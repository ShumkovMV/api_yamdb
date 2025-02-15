import datetime as dt

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.utils import IntegrityError
from rest_framework import serializers

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comments
)
from .constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH
)

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

    def validate(self, attrs):
        instance = CustomUser(**attrs)
        instance.clean()
        return attrs


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UnicodeUsernameValidator(),
        ],
        max_length=USERNAME_MAX_LENGTH,
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError({
                'username': 'Имя "me" не валидно'
            })
        return value

    def create(self, validated_data):
        try:
            user, _ = CustomUser.objects.get_or_create(**validated_data)
        except IntegrityError:
            error_mes = {}
            user_with_username = CustomUser.objects.filter(
                username__exact=validated_data.get('username'))
            if user_with_username.exists():
                error_mes.update(username=['Имя пользователя уже существует'])
            user_with_email = CustomUser.objects.filter(
                email__exact=validated_data.get('email'))
            if user_with_email.exists():
                error_mes.update(
                    email=['Пользователь с этим email уже существует'])
            raise serializers.ValidationError(error_mes)
        return user

    class Meta:
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = '__all__'

    def validate_genre(self, value):
        if value:
            return value
        raise serializers.ValidationError('Жанр не может быть пустым!')

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!')
        return value

    def to_representation(self, title):
        serializer = TitleGetSerializer(title)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True, allow_null=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs['title_id']
        if Review.objects.filter(author=user, title_id=title_id).exists():
            raise serializers.ValidationError(
                'Отзыв можно оставить только один раз!'
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comments
