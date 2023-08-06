from functools import partial

import graphene
from graphene.types.resolver import get_default_resolver
from graphene_django.utils import maybe_queryset

from .decorators import needs_permission
from .mixins import FilterMixin, PaginationMixin
from .utils import select_resolver


__all__ = ['ModelField', 'ModelListField', ]


class ModelField(graphene.Field):
    """
    Adds id and slug to the filter fields.  # todo: implement slug with natural key lookup

    .. code:
       class Query(graphene.ObjectType):
           user = ModelField(UserType)

    """

    def __init__(self, _type, id=graphene.ID(), required=False, *args, **kwargs):
        kwargs.update(id=id, )

        self.model_type = _type
        if required:
            _type = graphene.NonNull(_type)

        super(ModelField, self).__init__(_type, *args, **kwargs)

    @classmethod
    def model_resolver(cls, resolver, _type, root, info,
                       id=None,
                       **args):
        resolver_func = resolver.func if isinstance(resolver, partial) else resolver
        if resolver_func is get_default_resolver():
            # Use the get_model_instance() resolver defined on the type
            resolver = partial(_type.get_model_instance, resolver)

            if _type.get_perms() is not None:
                # Enforce permissions defined on the type
                resolver = needs_permission(*_type.get_perms())(resolver)

        parent_ret = resolver(root, info, id=id, **args)
        return parent_ret

    def get_resolver(self, parent_resolver):
        return partial(self.model_resolver, self.resolver or parent_resolver, self.get_type())

    def get_type(self):
        """ Return the type that we are using in the class resolver. """
        return self.model_type


class ModelPageListField(PaginationMixin, graphene.Field):
    """ Paginates a list of retrieved model types. """
    pass


class ModelFilterField(FilterMixin, graphene.Field):
    """ Filters a list of retrieved model types. """

    def __init__(self, _type, required=False, *args, **kwargs):
        type_meta = _type._meta

        if required:
            _type = graphene.NonNull(_type)

        super(ModelFilterField, self).__init__(graphene.List(_type), required=required, type_meta=type_meta, *args,
                                               **kwargs)

    def get_resolver(self, parent_resolver):
        return partial(self.filter_resolver, self.resolver or parent_resolver, self.get_type(), self._filter_set_class)


class ModelFilterPageField(FilterMixin, PaginationMixin, graphene.Field):
    """ Filters a list of retrieved model types and paginates the list. """

    @classmethod
    def filter_page_resolver(cls, resolver, _type, filter_set_class, root, info, **args):
        # Filter resolver is expecting the actual type, not the Paginator type
        partial_filter = partial(cls.filter_resolver, resolver, _type, filter_set_class)

        # Page resolver is expecting the Paginator type
        return cls.page_resolver(partial_filter, _type._meta.paginator, root, info, **args)

    def get_resolver(self, parent_resolver):
        return partial(self.filter_page_resolver, self.resolver or parent_resolver, self.get_type(),
                       self._filter_set_class)


# TODO: Factor out list resolver logic into a ListMixin?
class ModelListField(graphene.Field):
    """ Lists retrieved model types """

    def __init__(self, _type, *args, required=False, **kwargs):
        self.model_type = _type

        if required:
            _type = graphene.NonNull(_type)

        super(ModelListField, self).__init__(graphene.List(_type), required=required, *args, **kwargs)

    @classmethod
    def list_resolver(cls, resolver, _type, root, info, **args):
        selected_resolver = select_resolver(resolver, _type, root)
        return maybe_queryset(selected_resolver(root, info, **args))

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.resolver or parent_resolver, self.get_type())

    def get_type(self):
        """ Return the type that we are using in the class resolver. """
        return self.model_type
