from rest_framework import mixins, viewsets


class GetViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для просмотра  экземпляров и публикации """


class GetPostViewSet(GetViewSet, mixins.CreateModelMixin):
    """Вьюсет для просмотра экземпляров и публикации """
