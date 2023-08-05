"""
(C) 2019-2020 Alexander Forselius <alexander.forselius@buddhalow.com>
Licensed under MIT
"""

from django.http import JsonResponse
from django.shortcuts import render as django_render

from . import serialize


def render(request, template, data):
    if 'application/json' in request.META.get('HTTP_ACCEPT'):
        data = serialize(data, 5, 0)
        return JsonResponse(
            data
        )
    else:
        return django_render(request, template, data)
