from django.urls import include, path
from rest_framework import routers

from .views import (APIToken, CartView, DeleteToken, FavoriteView,
                    IngredientViewSet, SubscriptionView, RecipeViewSet,
                    TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = [
      path('users/<user_id>/subscribe/',
           SubscriptionView.as_view(), name='subscribe'),
      path('recipes/<recipe_id>/favorite/',
           FavoriteView.as_view(), name='favorite'),
      path('recipes/<recipe_id>/shopping_cart/',
           CartView.as_view(), name='cart'),
      path('', include(router.urls)),
      path('auth/token/login/', APIToken.as_view(), name='token'),
      path('auth/token/logout/', DeleteToken.as_view(), name='del_token'),
]
