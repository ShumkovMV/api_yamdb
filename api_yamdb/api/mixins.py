from rest_framework import mixins, viewsets, filters


class CreateListDestroyMixin(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):

    """Кастомный миксин для вьюсетов моделей Category и Genre."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
