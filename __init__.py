# coding: utf-8
from openstack_tools.yaml_scheme import load_scheme


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
