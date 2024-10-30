from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, registration, get_token

router_for_urls = DefaultRouter()
router_for_urls.register(r'users', UserViewSet, basename='user')

v1urlpatterns = [
    path('', include(router_for_urls.urls)),
    path('auth/register/', registration, name='registration'),
    path('auth/token/', get_token, name='get_token'),
]

urlpatterns = [
    path('v1/', include(v1urlpatterns)),
]
