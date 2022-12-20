from rest_framework.permissions import AllowAny

from users.models import User

from .mixins import GetPostViewSet
from .serializers import UserSerializer


class UserViewSet(GetPostViewSet):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
