from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    """Пермишн для  рецептов"""
    message = ('Для редактирования Вы должны  быть автором рецепта')

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user)
