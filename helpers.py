# coding: utf-8
from functools import wraps
from openstack_tools import settings

__author__ = 'morose'


@wraps
def cached_by_args(fn, _cache=dict()):

    def wrapper(*args, **kwargs):
        key = repr(args) + repr(kwargs)
        if key not in _cache or not any([args, kwargs]):
            _cache[key] = fn(*args, **kwargs)

        return _cache[key]

    return wrapper


def get_auth_from_settings():
    return {
        'auth_url': settings.auth.os_auth_url,
        'username': settings.auth.os_username,
        'password': settings.auth.os_password,
        'tenant_name': settings.auth.os_tenant,
    }
