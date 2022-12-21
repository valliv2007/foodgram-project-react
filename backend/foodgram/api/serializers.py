from rest_framework import exceptions, serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей"""
    password = serializers.CharField(required=True, write_only=True)
    # is_subscribed = serializers.BooleanField(required=False, default=False, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)
        read_only_fields = ('id', )


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
