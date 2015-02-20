# coding: utf-8
from functools import wraps
from celery_app import logger
from yaml_scheme import load_scheme

__author__ = 'morose'


@wraps
def cached_by_args(fn, _cache=dict()):

    def wrapper(*args, **kwargs):
        key = repr(args) + repr(kwargs)

        if key not in _cache or not any([args, kwargs]):
            _cache[key] = fn(*args, **kwargs)
            logger.debug('cache param')
        else:
            logger.debug('got cached param')
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
    SETTINGS_FILE = 'settings.yaml'

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
        return load_scheme(path)

    def __getattr__(self, item):
        result = self._params.get(item, self._def_value)
        if isinstance(result, dict):
            result = self.__class__(result)
        return result


settings = Settings()


class BaseEnum(object):

    values = None

    @classmethod
    def __contains__(self, item):
        return item in self.__class__.__dict__.values()

    @classmethod
    def __getitem__(self, item):
        return self.values[item]