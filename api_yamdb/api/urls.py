from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, 
    GenreViewSet, 
    TitleVeiwSet,
    UserViewSet,
    registration,
    get_token
)

router_v1 = DefaultRouter()
router_v1.register('titles', TitleVeiwSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('auth/register/', registration, name='registration'),
    path('auth/token/', get_token, name='get_token'),
]
