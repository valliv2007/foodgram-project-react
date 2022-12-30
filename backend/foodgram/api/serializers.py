import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import exceptions, serializers

from recipes.models import (Cart, Favorite, Ingredient,
                            IngredientRecipe, Recipe, Tag, TagRecipe)
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей"""
    password = serializers.CharField(required=True, write_only=True,
                                     max_length=150)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)
        read_only_fields = ('id', )


class UserSubscribeSerializer(UserSerializer):
    """Сериалайзер для пользователей c полем is_subscribed"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')
        model = User
        read_only_fields = ('id', )

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        return Subscription.objects.filter(user=self.context['request'].user,
                                           author=obj).exists()


class JWTTokenSerializer(serializers.Serializer):
    """Сериалайзер для получения токена"""

    password = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise exceptions.NotFound(
                'Такого пользователя не существует')
        if not User.objects.filter(password=data['password'],
                                   email=data['email']).exists():
            raise exceptions.ParseError(
                'Вы ввели неверный пароль')
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Сериалайзер для смены пароля"""

    current_password = serializers.CharField(max_length=150)
    new_password = serializers.CharField(max_length=150)

    def validate(self, data):
        if self.context['request'].user.password != data['current_password']:
            raise exceptions.ParseError(
                'Вы ввели неверный пароль')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name',  'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тэгов"""

    class Meta:
        model = Tag
        fields = ('id', 'name',  'color', 'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для  связи ингридиентов и рецептов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientRecipe
        read_only_fields = ('__all__', )


class Base64ImageField(serializers.ImageField):
    """Переопределение поля для кодировки изображений"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра рецептов"""
    tags = TagSerializer(many=True)
    author = UserSubscribeSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipes')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipe
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Favorite.objects.filter(user=self.context['request'].user,
                                       recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Cart.objects.filter(user=self.context['request'].user,
                                   recipe=obj).exists()


class FavoriteSerializer(serializers.Serializer):
    """Сериалайзер для  избранного и списка покупок"""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для для записи рецептов"""
    tags = serializers.ListField(write_only=True)
    ingredients = serializers.ListField(write_only=True)
    image = Base64ImageField()
    author = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate_ingredients(self, data):
        MIN_AMOUNT = 1
        for ingredient in data:
            if int(ingredient.get('amount')) < MIN_AMOUNT:
                raise serializers.ValidationError(
                    'Количество должно быть быть больше нуля')
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            tag_object = get_object_or_404(Tag, id=tag)
            TagRecipe.objects.create(tag=tag_object, recipe=recipe)
        for ingredient in ingredients:
            ingredient_object = get_object_or_404(
                Ingredient, id=ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=ingredient_object, recipe=recipe,
                amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            tag_object = get_object_or_404(Tag, id=tag)
            TagRecipe.objects.create(tag=tag_object, recipe=instance)
        for ingredient in ingredients:
            ingredient_object = get_object_or_404(
                Ingredient, id=ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=ingredient_object, recipe=instance,
                amount=ingredient['amount'])
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context['request']})
        return serializer.data


class RecipeSubcribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для  вывода рецептов в подписках"""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        read_only_fields = ('__all__',)


class SubscribtionSerializer(UserSubscribeSerializer):
    """Сериалайзер для вывода подписок"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        model = User
        read_only_fields = ('__all__',)

    def get_recipes(self, obj):
        request = self.context['request']
        recipe_limit = request.GET.get('recipes_limit')
        if recipe_limit:
            recipes = Recipe.objects.filter(author=obj)[:int(recipe_limit)]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = RecipeSubcribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
