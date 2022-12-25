from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets

from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import User, Subscription

from .mixins import GetPostViewSet
from .serializers import (ChangePasswordSerializer, FavoriteSerializer,
                          IngredientSerializer,
                          JWTTokenSerializer, RecipeReadSerializer,
                          TagSerializer, UserSerializer,
                          UserSubscribeSerializer)


class UserViewSet(GetPostViewSet):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.path != '/api/users/':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserSubscribeSerializer

    @action(detail=False, methods=('get',),
            url_name='me')
    def me(self, request, *args, **kwargs):
        serializer = UserSubscribeSerializer(request.user,
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',),
            url_name='subscriptions')
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(content_maker__user=request.user.id)
        serializer = UserSubscribeSerializer(queryset,
                                             context={'request': request},
                                             many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('post',),
            url_name='set_password')
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})
        if serializer.is_valid(raise_exception=True):
            request.user.password = serializer.data['new_password']
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингридиентами"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингридиентами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингридиентами"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author',)


class FavoriteView(APIView):
    """Вьюкласс для избранного"""

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=request.user, recipe=recipe):
            return Response(
                {'error': 'Вы уже добавили этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        deleted_favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe)
        if not deleted_favorite.exists():
            return Response(
                {'error': 'У вас нет этого рецепта в избранном'},
                status=status.HTTP_400_BAD_REQUEST)
        deleted_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    """Вьюкласс для списка покупок"""

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Cart.objects.filter(user=request.user, recipe=recipe):
            return Response(
                {'error': 'Вы уже добавили этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST)
        cart = Cart.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        deleted_cart = Cart.objects.filter(
            user=request.user, recipe=recipe)
        if not deleted_cart.exists():
            return Response(
                {'error': 'У вас нет этого рецепта в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        deleted_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
