from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, mixins, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .permissions import (
    ModerAdminAuthorPermission,
    IsAdminPermission,
    AnonReadOnlyOrIsAdminPermission,
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
from rest_framework.permissions import AllowAny
from .permissions import AnonReadOnlyOrIsAdminPermission, IsAdminPermission

from reviews.models import Title, Review, Comments, Category, Genre


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        ModerAdminAuthorPermission,
        AnonReadOnlyOrIsAdminPermission
    )
    pagination_class = PageNumberPagination
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
        ModerAdminAuthorPermission,
        AnonReadOnlyOrIsAdminPermission
    )
    pagination_class = PageNumberPagination

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


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'description', 'year', 'category', 'genre')

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [AnonReadOnlyOrIsAdminPermission()]
        return [AllowAny()]

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('-rating')


class CategoryViewSet(CreateListDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminPermission()]
        return [AllowAny()]


class GenreViewSet(CreateListDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AnonReadOnlyOrIsAdminPermission,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminPermission()]
        return [AllowAny()]


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = BaseUserSerializer

    lookup_field = 'username'
    permission_classes = (IsAdminPermission,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, permission_classes=(ModerAdminAuthorPermission,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    @action(detail=False, methods=['patch'], url_path='me')
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
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
