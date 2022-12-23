from rest_framework import exceptions, serializers

from users.models import User, Subscription
from recipes.models import Ingredient


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
    """Сериалайзер для cvtysw пароля"""

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
