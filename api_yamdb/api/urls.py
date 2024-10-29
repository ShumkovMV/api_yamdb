from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleVeiwSet


router_v1 = DefaultRouter()
router_v1.register('titles', TitleVeiwSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
