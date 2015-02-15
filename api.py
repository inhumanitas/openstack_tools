# coding: utf-8
from keystone_tools import auth_ks_client_by_pass

from openstack_tools import load_scheme
from openstack_tools.helpers import get_auth_from_settings
from openstack_tools.tasks import (
    get_heat_client_task, create_stack_by_template_task)


def create_stack_by_template_async(
        scheme_template, auth_info=None, stack_name=None, providing_args=None):
    u"""Run heat client"""
    keystone_client = auth_ks_client_by_pass(
        auth_info or get_auth_from_settings())

    chain = (
        get_heat_client_task.s(keystone_client) |
        create_stack_by_template_task.s(
            scheme_template, stack_name, providing_args)
    )
    return chain()


create_stack_by_template_async(
    load_scheme('hello_world.yaml'), stack_name='new_stack',
    providing_args={
        'key': u'',
        'image': u'cirros-0.3.3-x86_64',
        'flavor': u'm1.tiny',
        'private_network': u'',
    })