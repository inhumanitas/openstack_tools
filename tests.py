# coding: utf-8
import os
import testtools
import yaml

from openstack_tools.heat_tools.api import (
    get_orchestration_api_url, get_heat_client, create_stack_by_template,
    delete_stack, action_stack, StackActions, stack_info, stack_status)
from openstack_tools.helpers import get_auth_from_settings
from openstack_tools.keystone_tools.auth import auth_ks_client_by_pass
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
        self.hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )

        return super(HeatClientTests, self).setUp()

    def test_archestra_url(self):
        url = get_orchestration_api_url(self.ksclient)
        self.assertIsNotNone(url)

    def test_heat_client_has_stack(self):
        stack = [s for s in self.hc.stacks.list()]

        self.assertIsInstance(stack, list)

    def test_stack_create(self):
        stack_info = create_stack_by_template(
            self.hc, self.scheme,
            stack_name=self.new_stack_name, providing_args=self.scheme_args)

        self.assertIsNotNone(stack_info)

    # def test_stack_set_state(self):
    #     for stack in hc.stacks.list():
    #         if stack.stack_name == self.new_stack_name:
    #             self.assertIsNotNone(action_stack(hc, stack.id, StackActions.CHECK))

    def test_stack_info(self):
        for stack in self.hc.stacks.list():
            if stack.stack_name == self.new_stack_name:
                info = stack_info(self.hc, stack.id)
                self.assertIsNotNone(info)

    def test_stack_status(self):
        for stack in self.hc.stacks.list():
            if stack.stack_name == self.new_stack_name:
                result, status = stack_status(self.hc, stack)
                self.assertIsNotNone(result)

    def doCleanups(self):
        res = super(HeatClientTests, self).doCleanups()
        hc = get_heat_client(
            self.token,
            get_orchestration_api_url(self.ksclient)
        )

        for stack in hc.stacks.list():
            if stack.stack_name == self.new_stack_name:
                delete_stack(hc, stack.id)
        return res