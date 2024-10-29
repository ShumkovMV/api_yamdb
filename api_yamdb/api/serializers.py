import datetime as dt

from rest_framework import serializers

from .models import Category, Genre, Title


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value > year):
            raise serializers.ValidationError('Год выпуска не может быть '
                                              'больше текущего!')
        return value

    def get_rating(self, obj):
        return 0  # Вернуть среднее арифметическое рейтинга


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
