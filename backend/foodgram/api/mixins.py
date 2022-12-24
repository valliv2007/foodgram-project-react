from rest_framework import mixins, viewsets


class GetPostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для просмотра экземпляров и публикации """
