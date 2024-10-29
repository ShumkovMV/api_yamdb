import datetime as dt	
from django.contrib.auth import get_user_model	
from rest_framework import serializers	
from reviews.models import Comments, Review, Category, Genre, Title	

	
User = get_user_model()	
	
	
class CategorySerializer(serializers.ModelSerializer):

    class Meta:	
        model = Category	
        fields = ('name', 'slug',)	
	
	
class GenreSerializer(serializers.ModelSerializer):

    class Meta:	
        model = Genre	
        fields = ('name', 'slug',)	
	
	
class TitleSerializer(serializers.ModelSerializer):	
    rating = serializers.IntegerField(read_only=True)	
    description = serializers.CharField(allow_blank=True, required=False)	
    genre = serializers.SlugRelatedField(slug_field='slug',	required=True, many=True, queryset=Genre.objects.all())	
    category = serializers.SlugRelatedField(slug_field='slug', required=True, queryset=Category.objects.all())	
	
    class Meta:	
        model = Title	
        fields = (	
            'id', 'name', 'year', 'rating', 'description', 'genre',	
            'category',)	
	
    def to_representation(self, instance):	
        pass
	#валидацию здесь или отдельно 
	
class ReviewSerializer(serializers.ModelSerializer):	
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)	
	
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
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)	
	
    class Meta:	
        fields = ('id', 'text', 'author', 'pub_date',)	
        model = Comments	
	
	
class UserSerializer(serializers.ModelSerializer):	
    pass
