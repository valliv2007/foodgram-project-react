from django.urls import include, path
from rest_framework import routers

from .views import APIToken, UserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
urlpatterns = [
      path('', include(router.urls)),
      path('auth/token/login/', APIToken.as_view(), name='token'),
]
