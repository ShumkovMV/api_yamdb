from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from .pagination import PagePagination
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)

from reviews.models import Title, Review, Comments, Category, Genre		
from .serializers import (ReviewSerializer, CommentsSerializer, CategorySerializer, TitleSerializer, GenreSerializer, UserSerializer,)	
# импорты дописать и исправить
User = get_user_model()	


class TitleViewSet(viewsets.ModelViewSet):		
    serializer_class = TitleSerializer		
    permission_classes = (IsAdminOrReadOnly,)		
    pagination_class = PagePagination		
    filter_backends = (DjangoFilterBackend,)		
    filterset_class = TitleFilter		
		
    def get_queryset(self):		
        return Title.objects.annotate(		
            rating=Avg('reviews__score')		
        ).order_by('-rating')


class ReviewViewSet(viewsets.ModelViewSet):	
    serializer_class = ReviewSerializer	
    permission_classes = (	
        IsAuthorModeratorAdminOrReadOnly,	
        IsAuthenticatedOrReadOnly	
    )	
    pagination_class = PagePagination	
    filter_backends = set()	
	
    def get_queryset(self):	
        title_id = self.kwargs.get('title_id')	
        title = get_object_or_404(Title, pk=title_id)	
        return title.reviews.all()	
	
    def perform_create(self, serializer):	
        title_id = self.kwargs.get('title_id')	
        title = get_object_or_404(Title, pk=title_id)	
        user = self.request.user	
        serializer.save(author=user, title=title)	


class CommentViewSet(viewsets.ModelViewSet):		
    serializer_class = CommentsSerializer		
    permission_classes = (		
        IsAuthorModeratorAdminOrReadOnly,		
        IsAuthenticatedOrReadOnly		
    )		
    pagination_class = PagePagination		
		
    def get_queryset(self):		
        title_id = self.kwargs.get('title_id')		
        review_id = self.kwargs.get('review_id')		
        title = get_object_or_404(Title, pk=title_id)		
        review = get_object_or_404(Review, pk=review_id, title=title)		
        return Comments.objects.filter(review=review)		
		
    def perform_create(self, serializer):		
        title_id = self.kwargs.get('title_id')		
        review_id = self.kwargs.get('review_id')		
        title = get_object_or_404(Title, pk=title_id)		
        review = get_object_or_404(Review, pk=review_id, title=title)		
        serializer.save(author=self.request.user, review=review)	


class UserViewSet(viewsets.ModelViewSet):
    pass
		
