from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets, filters, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import EMAIL_SENDER
from .filters import TitleFilter
from .permissions import (
    AnonReadOnlyOrIsAdminPermission,
    IsAdminPermission,
    ModerAdminAuthorPermission,
)
from .serializers import (
    BaseUserSerializer,
    CategorySerializer,
    CommentsSerializer,
    GenreSerializer,
    RegistrationSerializer,
    ReviewSerializer,
    TitleGetSerializer,
    TitlePostSerializer,
    TokenSerializer,
)
from reviews.models import Category, Comments, Genre, Review, Title
from users.models import CustomUser


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    '''Кастомный viewset для вьюсетов моделей Category и Genre.'''
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class BaseSlugViewSet(CreateListDestroyViewSet):
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminPermission()]
        return [AllowAny()]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ModerAdminAuthorPermission,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        title_id = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title_id.reviews.all()

    def get_title(self, title_id):
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = self.get_title(title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (ModerAdminAuthorPermission,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_title(self, title_id):
        return get_object_or_404(Title, pk=title_id)

    def get_review(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        self.get_title(title_id)
        review_id = self.kwargs.get('review_id')
        review = self.get_review(review_id)
        return Comments.objects.filter(review=review)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        self.get_title(title_id)
        review_id = self.kwargs.get('review_id')
        review = self.get_review(review_id)
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminPermission()]
        return [AllowAny()]

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('-rating')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitlePostSerializer


class CategoryViewSet(BaseSlugViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(BaseSlugViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.order_by('username')
    serializer_class = BaseUserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdminPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, permission_classes=(ModerAdminAuthorPermission,))
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    @action(detail=False, methods=['patch'], url_path='me',
            permission_classes=(ModerAdminAuthorPermission,))
    def patch_self_info(self, request):
        user = request.user
        data = request.data.copy()
        if 'role' in data:
            data.pop('role')
        serializer = self.get_serializer(user, data=data, partial=True)
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
        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
