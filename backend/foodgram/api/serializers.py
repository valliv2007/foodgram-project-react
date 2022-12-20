from rest_framework import serializers

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
