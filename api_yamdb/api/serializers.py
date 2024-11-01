import datetime as dt

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.validators import ValidationError

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comments
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

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" не валидно')
        return value

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

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value < year):
            raise serializers.ValidationError('Год выпуска не может быть '
                                              'больше текущего!')
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

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
