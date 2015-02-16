# coding: utf-8
import uuid

from heatclient.client import Client
from heatclient.exc import HTTPConflict
from testtools.matchers import MismatchError

from openstack_tools.helpers import settings, StackState
from openstack_tools.tasks import logger

CLIENT_VERSION = '1'


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
        'stack_name': stack_name or unicode(uuid.uuid4()),
    }
    try:
        stack = heat_client.stacks.create(**params)
    except (MismatchError, HTTPConflict) as e:
        # already exist with this name
        logger.debug(e.message)
        stack = None

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


def set_stack_state(heat_client, stack_id, state):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param stack_id: stack name id
    :state

    """
    assert state in StackState, (
        'state argument must be one of the StackState value')
    fn = getattr(heat_client.actions, StackState.methods[state])
    try:
        result = fn(stack_id)
    except HTTPConflict as e:
        # The another action is in progress
        result = ('Failed to set state to stack with id '
                  '%s: %s' % (stack_id, e))
        logger.debug(result)

    return result