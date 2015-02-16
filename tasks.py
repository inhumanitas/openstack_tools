# coding: utf-8
from celery.utils.log import get_task_logger
from openstack_tools.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name='openstack_tools.tasks.get_heat_client_task')
def get_heat_client_task(keystone_client):
    u"""Create heat task instance"""
    from openstack_tools.heat_tools import (
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
    from heat_tools import validate_template

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
    from openstack_tools.heat_tools import create_stack_by_template

    stack = create_stack_by_template(
        heat_client, scheme_template,
        stack_name=stack_name, providing_args=providing_args)

    return stack
