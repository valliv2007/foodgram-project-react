from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from users.models import User

from .mixins import GetPostViewSet
from .serializers import JWTTokenSerializer, UserSerializer


class UserViewSet(GetPostViewSet):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=('get',),
            url_name='me', permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIToken(APIView):
    """Вьюкласс для получения токена"""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.data['username'])
        token = AccessToken.for_user(user)
        return Response(
                {'token': str(token)}, status=status.HTTP_200_OK)
