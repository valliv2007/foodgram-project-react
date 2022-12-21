from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from users.models import User, Subscription

from .mixins import GetPostViewSet
from .serializers import (JWTTokenSerializer, UserSerializer,
                          UserSubscribeSerializer)


class UserViewSet(GetPostViewSet):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Определение сериалайзера для произведений"""
        if self.action == 'create':
            return UserSerializer
        return UserSubscribeSerializer

    @action(detail=False, methods=('get',),
            url_name='me', permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        serializer = UserSubscribeSerializer(request.user,
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',),
            url_name='subscriptions', permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(content_maker__user=request.user.id)
        serializer = UserSubscribeSerializer(queryset,
                                             context={'request': request},
                                             many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIToken(APIView):
    """Вьюкласс для получения токена"""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, password=serializer.data['password'],
            email=serializer.data['email'])
        token = SlidingToken.for_user(user)
        return Response(
                {'token': str(token)}, status=status.HTTP_200_OK)


class DeleteToken(APIView):
    """Вьюкласс для удаления токена"""

    def post(self, request):
        token = request.auth
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionView(APIView):
    """Вьюкласс для подписки"""

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if author == request.user:
            return Response(
                {'error': 'Вы пытаетесь подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(user=request.user, author=author):
            return Response(
                {'error': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(user=request.user, author=author)
        serializer = UserSubscribeSerializer(author,
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        deleted_subscribtion = Subscription.objects.filter(user=request.user,
                                                           author=author)
        if not deleted_subscribtion.exists():
            return Response(
                {'error': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        deleted_subscribtion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
