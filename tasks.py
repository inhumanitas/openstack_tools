# coding: utf-8
from celery import Celery
from celery.utils.log import get_task_logger

celery = Celery('tasks', broker='amqp://guest@localhost//')

logger = get_task_logger(__name__)


@celery.task
def get_heat_client_task(keystone_client):
    u"""Create heat task instance"""
    from openstack_tools.heat_tools import (
        get_heat_client, get_orchestration_api_url)

    orch_url = get_orchestration_api_url(keystone_client)
    hc = get_heat_client(keystone_client.token, orch_url)
    return hc


@celery.task(name='validate_scheme_template_task')
def validate_scheme_template_task(heat_client, scheme_template):
    u"""Validate yaml template for stack
    :param heat_client: heat client instance
    :param scheme_template: yaml template represented by dict
    """
    from heat_tools import validate_template

    res = validate_template(heat_client, scheme_template)
    return res


@celery.task(name='create_stack_by_template_task')
def create_stack_by_template_task(heat_client, scheme_template,
                                  stack_name=None, providing_args=None):
    u"""Creates stack by yaml scheme template
    :param heat_client: heat client instance
    :param scheme_template: yaml scheme represented by dict
    :param stack_name: new stack name, generated itself if not provided
    :param providing_args: params for scheme_template
    :return stack
    """
    from heat_tools import create_stack_by_template

    stack = create_stack_by_template(
        heat_client, scheme_template, stack_name=None, providing_args=None)

    return stack
