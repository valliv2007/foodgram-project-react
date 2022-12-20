from rest_framework import mixins, viewsets


class GetPostViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для просмотра всех экземпляров,  публикации и удаления"""
