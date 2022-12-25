import base64

from django.core.files.base import ContentFile
from rest_framework import exceptions, serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
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
        if not User.objects.filter(password=data['password'],
                                   email=data['email']).exists():
            raise exceptions.NotFound(
                'Такого пользователя не существует')
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
    image = serializers.ImageField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time')
        model = Recipe
        read_only_fields = ('__all__', )
