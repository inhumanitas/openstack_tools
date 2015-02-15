# coding: utf-8
import os
import testtools
import yaml

from openstack_tools.heat_tools import (
    get_orchestration_api_url, get_heat_client, create_stack_by_template,
    delete_stack)
from openstack_tools.helpers import get_auth_from_settings
from openstack_tools.keystone_tools import auth_ks_client_by_pass
from openstack_tools.yaml_scheme import load_scheme, write_scheme

SCHEME_NAME = 'scheme.yaml'


class YamlTests(testtools.TestCase):
    OUT_FILE = 'scheme_out.yaml'

    scheme = u"""\
    version: 1900-01-01

    description: This is a simple YAML scheme example
    chapter:
    about:
    index:
      first: The first index
      second:
        - sub: sub_value
      another: [list]
    """

    def test_scheme_tools(self):
        u"""Test read/write functions for yaml"""
        write_scheme(yaml.load(self.scheme), self.OUT_FILE)
        self.assertEqual(load_scheme(self.OUT_FILE), yaml.load(self.scheme))
        os.remove(self.OUT_FILE)


class KeyStoneTests(testtools.TestCase):

    def test_authenticate(self):
        u"""retrieve keystone client and take token"""
        ksclient = auth_ks_client_by_pass(get_auth_from_settings())
        self.assertTrue(ksclient.authenticate())

    def test_tenant_id(self):
        ksclient = auth_ks_client_by_pass(get_auth_from_settings())
        os_tenant_id = ksclient.raw_token['token']['tenant']['id']
        self.assertIsNotNone(os_tenant_id)


class HeatClientTests(testtools.TestCase):

    def setUp(self):
        ks_client = auth_ks_client_by_pass(
            get_auth_from_settings())
        self.ksclient = ks_client.ksclient
        self.token = ks_client.token
        self.new_stack_name = 'stack1'
        # self.scheme = load_scheme('scheme.yaml')
        self.scheme = load_scheme('hello_world.yaml')
        self.scheme_args = {
            'key': u'',
            'image': u'cirros-0.3.3-x86_64',
            'flavor': u'm1.tiny',
            'private_network': u'',
        }
        return super(HeatClientTests, self).setUp()

    def test_archestra_url(self):

        url = get_orchestration_api_url(self.ksclient)
        self.assertIsNotNone(url)

    def test_heat_client(self):
        hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )
        self.assertIsNotNone(hc)

    def test_heat_client_has_stack(self):
        hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )
        stack = [s for s in hc.stacks.list()]

        self.assertIsInstance(stack, list)

    def test_stack_create(self):
        hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )

        stack_info = create_stack_by_template(
            hc, self.scheme,
            stack_name=self.new_stack_name, providing_args=self.scheme_args)

        self.assertIsNotNone(stack_info)

    def test_stack_delete_all(self):
        hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )

        for stack in hc.stacks.list():
            if stack.stack_name == self.new_stack_name:
                print delete_stack(hc, stack.id)
