from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets

from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from .mixins import GetPostViewSet
from .paginators import RecipePagination
from .permissions import RecipePermission
from .serializers import (ChangePasswordSerializer, FavoriteSerializer,
                          IngredientSerializer,
                          JWTTokenSerializer, RecipeSerializer,
                          RecipeReadSerializer, SubscribtionSerializer,
                          TagSerializer, UserSerializer,
                          UserSubscribeSerializer)


class UserViewSet(GetPostViewSet):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()
    pagination_class = RecipePagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
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
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribtionSerializer(
                page, many=True, context={'request': request},)
            return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=('post',),
            url_name='set_password', permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})
        serializer.is_valid(raise_exception=True)
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
                {'auth_token': str(token)}, status=status.HTTP_200_OK)


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
        if Subscription.objects.filter(
             user=request.user, author=author).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(user=request.user, author=author)
        serializer = SubscribtionSerializer(author,
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
    """Вьюсет для работы с ингредиентами"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тэгами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, RecipePermission)
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=('get',),
            url_name='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=self.request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount_sum=Sum('amount')).order_by('ingredient__name')
        file_content = 'СПИСОК ПОКУПОК \n \n'
        number_line = 0
        for ingredient in ingredients:
            number_line += 1
            file_content += (
                f"{number_line}. {ingredient.get('ingredient__name')} "
                f"({ingredient.get('ingredient__measurement_unit')}) - "
                f"{ingredient.get('amount_sum')} \n")
        file_content += '\nУдачных покупок и приятного аппетита! Ваш foodgram'

        return HttpResponse(
            file_content, content_type='text/plain, charset=utf8',
            status=status.HTTP_200_OK)


class FavoriteView(APIView):
    """Вьюкласс для избранного"""
    MODEL = Favorite

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.MODEL.objects.filter(
             user=request.user, recipe=recipe).exists():
            return Response(
                {'error': 'Вы уже добавили этот рецепт'},
                status=status.HTTP_400_BAD_REQUEST)
        favorite = self.MODEL.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        deleted = self.MODEL.objects.filter(
            user=request.user, recipe=recipe)
        if not deleted.exists():
            return Response(
                {'error': 'У вас нет этого рецепта'},
                status=status.HTTP_400_BAD_REQUEST)
        deleted.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(FavoriteView):
    """Вьюкласс для списка покупок"""
    MODEL = Cart
