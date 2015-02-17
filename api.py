# coding: utf-8
from keystone_tools import auth_ks_client_by_pass

from openstack_tools.helpers import get_auth_from_settings
from openstack_tools.tasks import (
    get_heat_client_task, create_stack_by_template_task)
from openstack_tools.yaml_scheme import load_scheme


def create_stack_by_template_async(
        scheme_template, auth_info=None, stack_name=None, providing_args=None):
    u"""Creates heat client then creates stack by template"""
    ksclient = auth_ks_client_by_pass(
        auth_info or get_auth_from_settings())
    keystone_client = ksclient.ksclient
    chain = (
        get_heat_client_task.s(keystone_client) |
        create_stack_by_template_task.s(
            scheme_template, stack_name, providing_args)
    )

    async_result = chain()

    return async_result

if __name__ == '__main__':

    # providing_args = {
    #     'key': u'',
    #     'image': u'cirros-0.3.3-x86_64',
    #     'flavor': u'm1.tiny',
    #     'private_network': u'',
    # }

    providing_args = {
        'key_name': u'',
        'image': u'cirros-0.3.3-x86_64',
        'flavor': u'm1.tiny',
        'public_net_id': '14625fbc-84bd-4359-a1b3-94a4dd9d5625',
        'private_net_id': '4e66becc-6df1-4c8a-8905-477b87d73e14',
        'private_subnet_id': '229091ce-163f-436f-ac1d-3d65e352026f',
    }

    create_stack_by_template_async(
        load_scheme('scheme.yaml'), stack_name='test_stack1',
        providing_args=providing_args)
