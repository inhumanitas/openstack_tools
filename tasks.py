# coding: utf-8
from time import sleep
from heat_tools.helpers import StackStatuses

from openstack_tools.celery_app import celery_app, logger


@celery_app.task(name='openstack_tools.tasks.get_heat_client_task')
def get_heat_client_task(keystone_client):
    u"""Create heat task instance"""
    from openstack_tools.heat_tools.api import (
        get_heat_client, get_orchestration_api_url)

    orch_url = get_orchestration_api_url(keystone_client)
    hc = get_heat_client(keystone_client.auth_token, orch_url)
    return hc


@celery_app.task(name='openstack_tools.tasks.validate_scheme_template_task')
def validate_scheme_template_task(heat_client, scheme_template):
    u"""Validate yaml template for stack
    :param heat_client: heat client instance
    :param scheme_template: yaml template represented by dict
    """
    from openstack_tools.heat_tools.api import validate_template

    res = validate_template(heat_client, scheme_template)
    return res


@celery_app.task(name='openstack_tools.tasks.create_stack_by_template_task')
def create_stack_by_template_task(heat_client, scheme_template,
                                  stack_name=None, providing_args=None):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param scheme_template: yaml scheme represented by dict
    :param stack_name: new stack name, generated itself if not provided
    :param providing_args: params for scheme_template
    :return stack
    """
    from openstack_tools.heat_tools.api import create_stack_by_template

    stack = create_stack_by_template(
        heat_client, scheme_template,
        stack_name=stack_name, providing_args=providing_args)

    return stack


@celery_app.task(name='openstack_tools.tasks.stack_status_task')
def track_stack_status_task(stack, heat_client,
                            timeout=None, watch_status=StackStatuses.SUCCESS,
                            tick_time=10):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param stack: new stack name, generated itself if not provided
    :return stack
    """
    from openstack_tools.heat_tools.api import stack_status

    def check_time_out():
        # TODO make timeout run out mechanizm
        return True

    status = None
    statuses = [
        StackStatuses[watch_status],
        StackStatuses[StackStatuses.FAILURE],
        StackStatuses[StackStatuses.SUCCESS],
    ]
    statuses = set(statuses)
    trackker_msg = 'tracking tick....'
    while check_time_out() and status not in statuses:
        status, info = stack_status(heat_client, stack)
        logger.info(' '.join([trackker_msg, status,  info]))
        sleep(tick_time)
    logger.info('Tracking finished')
    return stack
