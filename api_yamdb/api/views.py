from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (
    IsAuthorModeratorAdminOrReadOnly,
    IsAdminPermission,
    IsAuthenticatedOrReadOnly
)

from api_yamdb.settings import EMAIL_SENDER
from users.models import CustomUser

from .mixins import CreateListDestroyMixin

from .serializers import (
    RegistrationSerializer,
    TokenSerializer,
    BaseUserSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentsSerializer
)

from .permissions import AnonReadOnlyOrIsAdminPermission, IsAdminPermission

from .models import Category, Genre, Title
from reviews.models import Title, Review, Comments, Category, Genre


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


class TitleVeiwSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')


class CategoryViewSet(CreateListDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(CreateListDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'
    permission_classes = (IsAdminPermission,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=BaseUserSerializer,
    )
    def self_info(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @self_info.mapping.patch
    def patch_self_info(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def registration(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация аккаунта',
        message=f'Код подтверждения: {confirmation_code}',
        from_email=EMAIL_SENDER,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        CustomUser,
        username=serializer.validated_data['username']
    )

    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
