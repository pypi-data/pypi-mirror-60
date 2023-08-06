import copy
import uuid
from typing import Tuple

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import ManyToManyRel


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True  # уже unique
    )

    class Meta:
        abstract = True


class NestedUpdateOrCreateModelManager(models.Manager):
    RELATED_OBJECT_NAMES = []
    UPDATE_OR_CREATE_FILTER_FIELDS = {}
    RECREATE_OBJECT_NAMES = []

    def __get_nested_objects_data(self, object_data: dict) -> Tuple[dict, dict]:
        nested_objects_data = dict()
        fields = self.model._meta.get_fields()
        for field in fields:
            try:
                related_name = field.related_name
                if (
                    self.RELATED_OBJECT_NAMES
                    and related_name not in self.RELATED_OBJECT_NAMES
                ):
                    continue
                if related_name in object_data:
                    nested_objects_data[related_name] = {
                        "field_object": field,
                        "object_data": object_data.pop(related_name),
                    }
            except AttributeError:
                continue
        return object_data, nested_objects_data

    def update_or_create_nested_objects(  # noqa: C901
        self, instance, nested_objects_data, update: bool = False
    ):
        for field_name, d in nested_objects_data.items():
            field_object = d["field_object"]
            object_data = d["object_data"]
            model = field_object.field.model
            related_field_name = field_object.field.name

            if field_object.one_to_one:
                object_data = [object_data]
                all_qs = field_object.field.model.objects.none()
            else:
                all_qs = getattr(instance, field_name).all()

            # Remove old objects before recreate
            if field_name in self.RECREATE_OBJECT_NAMES:
                all_qs.delete()

            # Create or update objects
            for data in object_data:
                defaults = data
                kwargs = {related_field_name: instance}
                if not update or field_name in self.RECREATE_OBJECT_NAMES:
                    model.objects.create(**kwargs, **defaults)
                else:
                    # Get filter fields of nested model
                    related_field_filter = self.UPDATE_OR_CREATE_FILTER_FIELDS.get(
                        field_name
                    )
                    if related_field_filter:
                        for field in related_field_filter:
                            kwargs[field] = defaults.pop(field, None)
                    # Get m2m field data
                    m2m_fields = dict()
                    for field in defaults:
                        try:
                            field_obj = model._meta.get_field(field)
                            if isinstance(field_obj.remote_field, ManyToManyRel):
                                m2m_fields[field] = defaults.pop(field)
                        except FieldDoesNotExist:
                            continue
                    # Create nested object
                    obj, created = model.objects.update_or_create(
                        **kwargs, defaults=defaults
                    )
                    # Update m2m fields
                    if m2m_fields:
                        for m2m_field_name, m2m_field_data in m2m_fields.items():
                            m2m_field = getattr(obj, m2m_field_name)
                            m2m_field.set(m2m_field_data)
                    # Filter qs for delete not existed objects
                    delete_filter_kwargs = copy.deepcopy(kwargs)
                    delete_filter_kwargs.pop(related_field_name)
                    if delete_filter_kwargs:
                        all_qs = all_qs.exclude(**delete_filter_kwargs)

            # Delete not existed nested objects
            if update and field_name not in self.RECREATE_OBJECT_NAMES:
                if all_qs:
                    all_qs.delete()

    def create(self, **kwargs):
        create_object_data, nested_objects_data = self.__get_nested_objects_data(
            object_data=kwargs
        )
        instance = super().create(**create_object_data)
        if nested_objects_data:
            self.update_or_create_nested_objects(instance, nested_objects_data)
        return instance

    def update_or_create(self, defaults=None, **kwargs):
        nested_objects_data = None
        if defaults:
            defaults, nested_objects_data = self.__get_nested_objects_data(defaults)
        instance, created = super().update_or_create(defaults=defaults, **kwargs)
        if nested_objects_data:
            self.update_or_create_nested_objects(
                instance, nested_objects_data, update=True
            )
        return instance, created
