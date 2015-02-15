# coding: utf-8
import yaml

__author__ = 'valiullin'


def write_scheme(scheme, file_name):
    u"""Writes yaml object scheme into file
     :param scheme: loaded yaml scheme
     :param file_name: file path string
    """
    assert isinstance(scheme, dict)
    assert isinstance(file_name, basestring)

    with open(file_name, 'w') as fh:
        yaml.dump(scheme, stream=fh)


def load_scheme(scheme_path):
    u"""Load yaml scheme from file
    :param scheme_path: file path
    :rtype: dict
    """
    assert isinstance(scheme_path, basestring)

    with open(scheme_path) as template_file:
        scheme = yaml.load(template_file)
    return scheme