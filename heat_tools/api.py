# coding: utf-8
import uuid

from heatclient.client import Client
from heatclient.exc import HTTPConflict
from heatclient.v1.stacks import Stack
from requests.exceptions import MissingSchema
from testtools.matchers import MismatchError
from celery_app import logger
from heat_tools.helpers import StackActions

from openstack_tools.helpers import settings


CLIENT_VERSION = '1'


class HeatClientException(Exception):
    pass


def get_orchestration_api_url(
        keystone_client, service_type="orchestration", endpoint_type='publicURL'):

    url = keystone_client.service_catalog.url_for(
        service_type=service_type,
        endpoint_type=endpoint_type,
    )
    return url


def get_heat_client(token, orchestration_api_url=''):
    """Return heat client.
    :param token: keystone client auth token
    :return heat client instance
    """
    try:
        # TODO find out Endpoint type, use it here
        client = Client(
            CLIENT_VERSION,
            endpoint=orchestration_api_url,
            token=token,
            auth_url=settings.auth.os_auth_url,
            # timeout=CONF.openstack_client_http_timeout,
            # insecure=CONF.https_insecure,
            # cacert=CONF.https_cacert
        )
    except Exception as e:
        logger.debug(e.message)
        client = None
        raise HeatClientException(e)

    return client


def create_stack_by_template(heat_client, scheme_template,
                             stack_name=None, providing_args=None):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param scheme_template: yaml scheme represented by dict
    :param stack_name: new stack name, generated itself if not provided
    :param providing_args: params for scheme_template
    :return stack
    """
    params = {
        "template": scheme_template,
        'parameters': providing_args,
        'stack_name': stack_name or 'stack'+unicode(uuid.uuid4()),
    }
    try:
        stack = heat_client.stacks.create(**params)
    except (MismatchError, HTTPConflict) as e:
        # already exist with this name
        logger.info(e.message)
        stack = None
        raise HeatClientException(e)
    except MissingSchema as e:
        stack = None
        raise HeatClientException(e)

    return stack


def validate_template(heat_client, scheme_template):
    u"""Validate yaml template for stack
    :param heat_client: heat client instance
    :param scheme_template: yaml template represented by dict
    """
    params = {
        "template": scheme_template,
        # 'parameters': provided_params,
        'stack_name': 'test1',
    }
    res = heat_client.stacks.validate(**params)
    # TODO learn how to validate results
    return True


def has_stack_with_id(heat_client, stack_id):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param stack_id: stack name id
    :return bool
    """
    stacks = [s for s in heat_client.stacks.list() if s.id == stack_id]
    return stacks > 0


def delete_stack(heat_client, stack_id):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param stack_id: stack name id
    """
    if has_stack_with_id(heat_client, stack_id):
        heat_client.stacks.delete(stack_id)


def action_stack(heat_client, stack, action):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param stack: stack name id
    :state

    """
    if action not in StackActions:
        raise ValueError('state param is not recognized')

    stack_id = stack
    if isinstance(stack, dict):
        stack_id = stack.get('stack').get('id')

    fn = getattr(heat_client.actions, StackActions.methods[action])
    try:
        result = fn(stack_id)
    except HTTPConflict as e:
        # The another action is in progress
        result = ('Failed to set state to stack with id '
                  '%s: %s' % (stack, e))
        logger.debug(result)
        raise HeatClientException(e)

    return result


def stack_info(heat_client, stack):
    u"""Retrieve stack information"""
    stack_id = stack
    if isinstance(stack, Stack):
        stack_id = stack.id

    if isinstance(stack, dict):
        stack_id = stack.get('stack').get('id')

    info = heat_client.stacks.get(stack_id)
    return info


def stack_status(heat_client, stack):
    u"""Retrieve stack information"""

    stack_instance = stack_info(heat_client, stack)
    result = None, 'undefined'
    if stack_instance:
        result = (stack_instance.stack_status,
                  stack_instance.stack_status_reason)
    return result