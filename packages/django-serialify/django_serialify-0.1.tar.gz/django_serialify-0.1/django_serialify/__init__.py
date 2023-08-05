"""
(C) 2019-2020 Alexander Forselius <alexander.forselius@buddhalow.com>
Licensed under MIT
"""

from datetime import date, datetime

from django.db.models import Model, QuerySet
from django.db.models.fields.files import FieldFile


def _get_field_id(
    field
):
    return field.name


def serialize(data, maximum_depth=0, level=0):
    """
    Serializes dicts and django models to dict
    :param data: The data
    :param maximum_depth:  Maximum recursion depth
    :param level: Current level
    :return: A dict
    """
    result = None
    if isinstance(data, dict):
        result = {}
        for attr in data.keys():
            if attr.startswith('_'):
                continue
            result[attr] = serialize(data[attr], maximum_depth, level + 1)
    elif isinstance(data, list):
        result = []
        for item in data:
            result.append(serialize(item, maximum_depth, level + 1))
    elif isinstance(data, Model):
        if level > maximum_depth:
            return data.id
        result = {}
        attributes = dir(data)
        for attr in attributes:
            if attr.startswith('_'):
                continue
            if hasattr(data, '_meta'):
                if attr in map(_get_field_id, data._meta.fields):
                    value = getattr(data, attr, None)
                    serialized_value = serialize(value, maximum_depth, level + 1)
                    result[attr] = serialized_value
    elif isinstance(data, QuerySet):
        result = []
        for item in data.all():
            result.append(serialize(item))
    elif isinstance(data, date):
        result = data.strftime('%Y-%m-%d')
    elif isinstance(data, datetime):
        result = data.isoformat()
    elif isinstance(data, FieldFile):
        result = None
    else:
        result = data
    return result
