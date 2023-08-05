from typing import Type
from django.db.models import Model
from graphene import ObjectType
from graphene_django_extras import (
    DjangoObjectType,
    DjangoSerializerMutation,
    DjangoListObjectType,
    DjangoListObjectField,
    LimitOffsetGraphqlPagination,
)
from graphene_django_extras.registry import get_global_registry
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from typedecorator import Nullable

from generate_graphene.config import DEFAULT_FILTERS_FIELDS
from generate_graphene.utils import (
    get_model_name,
    get_type_name,
    get_type_list_name,
    AbstractModelSerializerMutation,
    AuthDjangoFilterListField,
    AuthDjangoObjectField,
    AuthDjangoListObjectField,
    set_optionally,
)


class OverwriteLimitOffsetGraphqlPagination(LimitOffsetGraphqlPagination):
    def paginate_queryset(self, qs, **kwargs):  # subclass because there was a bug
        limit = _nonzero_int(
            kwargs.get(self.limit_query_param, None), strict=True, cutoff=self.max_limit
        )

        if limit is None:
            return qs

        order = kwargs.pop(self.ordering_param, None) or self.ordering
        if order:
            if "," in order:
                order = order.strip(",").replace(" ", "").split(",")
                if order.__len__() > 0:
                    qs = qs.order_by(*order)
            else:
                qs = qs.order_by(order)

        offset = kwargs.get(self.offset_query_param, 0)

        return qs[offset : offset + limit]



class GenerateGraphene:
    def __init__(self):
        self._object_types = dict()
        self._object_list_types = dict()
        self._model_serializers = dict()
        self._model_mutations = dict()
        self._model_excluded_fields = dict()
        self._models_to_register = list()

    _object_types = None
    _model_serializers = None
    _model_mutations = None
    _model_excluded_fields = None
    _models_to_register = None

    def exclude_single_field(self, m: Type[Model]) -> Type[Model]:
        """
        Query wont include a field to query a single instance for the passed model
        """
        self._exclude_field(m, "single")
        return m

    def exclude_pagination_field(self, m: Type[Model]) -> Type[Model]:
        """
        Query wont include a field to query a list for the passed model
        """
        self._exclude_field(m, "pagination")
        return m

    def exclude_list_field(self, m: Type[Model]) -> Type[Model]:
        """
        Query wont include a field to query a list for the passed model
        """
        self._exclude_field(m, "list")
        return m

    def exclude_create_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to create an instance
        """
        self._exclude_field(m, "create")
        return m

    def exclude_update_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to update an instance
        """
        self._exclude_field(m, "update")
        return m

    def exclude_delete_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to delete an instance
        """
        self._exclude_field(m, "delete")
        return m

    def get_is_excluded_field(self, model_name: str, field_name: str) -> bool:
        return (
                model_name in self._model_excluded_fields
                and field_name in self._model_excluded_fields[model_name]
        )

    def register_model(self, m: Type[Model]) -> Type[Model]:
        """
        DjangoObjectType and ModelSerializer will be generated for this model,
        unless these are already manually created and registered to this class.

        By default all operations will be possible:
            - Query single instance
            - Query list of instances
            - Create mutation
            - Read mutation
            - Update mutation
        """
        if not issubclass(m, Model):
            raise Exception('Expected subclass of "Model", got {}'.format(m))

        if m not in self._models_to_register:
            self._models_to_register.append(m)

        return m

    def set_mutation(
            self, model_mutation: Type[DjangoSerializerMutation]
    ) -> Type[DjangoSerializerMutation]:
        """
        Passed DjangoSerializerMutation will be used when creating graphene mutation fields.

        By default the following operations will be possible:
            - Create mutation
            - Read mutation
            - Update mutation
        """
        model = getattr(model_mutation._meta, "model")
        model_name = get_model_name(model)

        if model_name in self._model_mutations:
            raise Exception(
                "model_serializers already contains a serializer for {}".format(
                    model_name
                )
            )

        if not issubclass(model_mutation, DjangoSerializerMutation):
            raise Exception(
                'Expected subclass of "DjangoSerializerMutation", got {}'.format(
                    model_mutation
                )
            )

        self._model_mutations[model_name] = model_mutation
        return model_mutation

    def register_serializer(
            self, model_serializer: Type[ModelSerializer]
    ) -> Type[ModelSerializer]:
        """
        Passed ModelSerializer will be used when creating DjangoSerializerMutation.
        You will still have to call 'register_serializer' or 'register_model' to create mutation fields
        """
        model = getattr(model_serializer.Meta, "model")
        model_name = get_model_name(model)

        if model_name in self._model_serializers:
            raise Exception(
                "model_serializers already contains a serializer for {}".format(
                    model_name
                )
            )

        if not issubclass(model_serializer, ModelSerializer):
            raise Exception(
                'Expected subclass of "ModelSerializer", got {}'.format(
                    model_serializer
                )
            )

        self._model_serializers[model_name] = model_serializer
        return model_serializer

    def register_object_type(
            self, object_type: Type[DjangoObjectType]
    ) -> Type[DjangoObjectType]:
        """
        By default the following operations will be possible:
            - Query single instance
            - Query list of instances
        """
        if not issubclass(object_type, DjangoObjectType):
            raise Exception(
                'Expected subclass of "DjangoObjectType", got {}'.format(object_type)
            )

        model = object_type._meta.model
        model_name = get_model_name(model)
        type_name = get_type_name(model_name)
        registry = get_global_registry()
        if registry.get_directive(type_name):
            raise Exception(
                '{} already is a registered type'.format(type_name)
            )

        self._object_types[model_name] = object_type
        self.register_model(model)
        return object_type

    def register_object_list_type(
            self, object_type: Type[DjangoListObjectField]
    ) -> Type[DjangoListObjectField]:
        """
        By default the following operations will be possible:
            - Query single instance
            - Query list of instances
        """
        if not issubclass(object_type, DjangoListObjectType):
            raise Exception(
                'Expected subclass of "DjangoListObjectField", got {}'.format(
                    object_type
                )
            )

        model = object_type._meta.model
        self._object_list_types[get_model_name(model)] = object_type
        return object_type

    def get_object_list_type(self, m: Type[Model]) -> Type[DjangoObjectType]:
        self._create_object_list_type(m)
        return self._object_list_types[get_model_name(m)]

    def get_model_serializer(self, m: Type[Model]) -> Type[ModelSerializer]:
        model_name = get_model_name(m)

        if model_name in self._model_serializers:
            return self._model_serializers[model_name]

        class ModelSerializer(serializers.ModelSerializer):
            class Meta:
                name = model_name
                model = m
                exclude = []

        self._model_serializers[model_name] = ModelSerializer
        return ModelSerializer

    def register_graphql_objects(
            self,
            input_query: Nullable(Type[ObjectType]),
            input_mutations: Nullable(Type[ObjectType]),
    ) -> [Type[ObjectType], Type[ObjectType]]:

        # copy input so we dont change original query/mutations
        class CopiedQuery(input_query, ObjectType):
            pass

        class CopiedMutations(input_mutations, ObjectType):
            pass

        for model in self._models_to_register:
            model_name = get_model_name(model)

            # Paginated field
            if not self.get_is_excluded_field(model, "pagination"):
                object_list_type = self.get_object_list_type(model)
                optional_s = "s" if model_name[-1] != "s" else ""
                field_list_name = "paginated_{}{}".format(model_name, optional_s)
                field = AuthDjangoListObjectField(object_list_type)
                set_optionally(CopiedQuery, field_list_name, field)

            if not self.get_is_excluded_field(model_name, "single"):
                object_type = self.get_object_type(model)
                field = AuthDjangoObjectField(object_type)
                field_name = model_name
                set_optionally(CopiedQuery, field_name, field)

            if not self.get_is_excluded_field(model_name, "list"):
                object_type = self.get_object_type(model)
                optional_s = "s" if model_name[-1] != "s" else ""
                field = AuthDjangoFilterListField(object_type)
                field_list_name = "{}{}".format(model_name, optional_s)
                set_optionally(CopiedQuery, field_list_name, field)

            # Create create/delete/update fields, if they dont exist and are not excluded
            if not self.get_is_excluded_field(model_name, "create"):
                mutation_class = self.get_mutation_class(model)
                create_name = "create_{}".format(model_name)
                field = mutation_class.CreateField()
                set_optionally(CopiedMutations, create_name, field)

            if not self.get_is_excluded_field(model_name, "update"):
                mutation_class = self.get_mutation_class(model)
                update_name = "update_{}".format(model_name)
                field = mutation_class.UpdateField()
                set_optionally(CopiedMutations, update_name, field)

            if not self.get_is_excluded_field(model_name, "delete"):
                mutation_class = self.get_mutation_class(model)
                delete_name = "delete_{}".format(model_name)
                field = mutation_class.DeleteField()
                set_optionally(CopiedMutations, delete_name, field)

        # recompose into ObjectType
        class Query(CopiedQuery, ObjectType):
            pass

        class Mutations(CopiedMutations, ObjectType):
            pass

        return Query, Mutations

    def _exclude_field(self, m: Type[Model], field_name: str):
        model_name = get_model_name(m)

        if not model_name in self._model_excluded_fields:
            self._model_excluded_fields[model_name] = list()

        self._model_excluded_fields[model_name].append(field_name)

    def get_mutation_class(self, m: Type[Model]):
        model_name = get_model_name(m)

        if model_name in self._model_mutations:
            return self._model_mutations[model_name]

        class ModelSerializerMutation(AbstractModelSerializerMutation):
            class Meta:
                name = "{}Mutation".format(model_name)
                input_field_name = "{}Input".format(model_name)
                serializer_class = self.get_model_serializer(m)

        self._model_mutations[model_name] = ModelSerializerMutation
        return ModelSerializerMutation

    def get_object_type(self, m: Type[Model]):
        registry = get_global_registry()
        model_name = get_model_name(m)
        type_name = get_type_name(model_name)
        found_type = registry.get_directive(type_name)

        if found_type:
            return found_type

        if model_name in self._object_types:
            return self._object_types[model_name]

        class DjangoObjectTypeSubclass(DjangoObjectType):
            class Meta:
                filter_fields = DEFAULT_FILTERS_FIELDS
                name = type_name
                model = m

        self._object_types[model_name] = DjangoObjectTypeSubclass
        return DjangoObjectTypeSubclass

    def _create_object_list_type(self, m: Type[Model]):
        model_name = get_model_name(m)

        if model_name in self._object_list_types:
            return

        registry = get_global_registry()
        model_name = get_model_name(m)
        type_name = get_type_name(model_name)
        found_type = registry.get_directive(type_name)
        if found_type:
            self._object_list_types[model_name] = found_type
            return

        class DjangoObjectTypeSubclass(DjangoListObjectType):
            class Meta:
                filter_fields = DEFAULT_FILTERS_FIELDS
                name = get_type_list_name(model_name)
                model = m
                pagination = OverwriteLimitOffsetGraphqlPagination()

        self._object_list_types[model_name] = DjangoObjectTypeSubclass
