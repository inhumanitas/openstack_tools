# coding: utf-8
from functools import wraps
from openstack_tools import yaml_scheme


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


class SettingsException(Exception):
    def __init__(self, msg, *args, **kwargs):
        super(SettingsException, self).__init__(*args, **kwargs)
        self.msg = msg

    def __str__(self):
        return self.msg or self.__class__.__doc__


class Settings(object):
    u"""Provides simple settings attributes"""
    SETTINGS_FILE = '/home/morose/work/git/openstack_tools/settings.yaml'

    def __init__(self, init_params=None, default_value=None):
        if init_params:
            loaded = init_params
        else:
            try:
                loaded = self.load_params(self.SETTINGS_FILE)
            except IOError:
                raise SettingsException('Settings file loading error')

        self._params = loaded
        self._def_value = default_value

    @staticmethod
    def load_params(path):
        return yaml_scheme.load_scheme(path)

    def __getattr__(self, item):
        result = self._params.get(item, self._def_value)
        if isinstance(result, dict):
            result = self.__class__(result)
        return result
settings = Settings()


class _StackStateCls():

    SUSPEND = 1
    RESUME = 2
    CANCEL_UPDATE = 3
    CHECK = 4

    methods = {
        SUSPEND: 'suspend',
        RESUME: 'resume',
        CANCEL_UPDATE: 'cancel_update',
        CHECK: 'check',

    }

    def __contains__(self, item):
        return item in self.__class__.__dict__.values()

StackState = _StackStateCls()