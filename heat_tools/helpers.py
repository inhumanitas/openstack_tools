# coding: utf-8
from openstack_tools.helpers import BaseEnum

__author__ = 'morose'


class _StackActionsCls(BaseEnum):
    SUSPEND = 1
    RESUME = 2
    CANCEL_UPDATE = 3
    CHECK = 4

    methods = {
        SUSPEND: 'suspend',
        RESUME: 'resume',
        CANCEL_UPDATE: 'cancel_update',
        CHECK: 'check',

    }

StackActions = _StackActionsCls()


class _StackStatuses(BaseEnum):
    SUCCESS = 1
    FAILURE = 2
    IN_PROGRESS = 3

    values = {
        SUCCESS: 'CREATE_COMPLETE',
        FAILURE: 'CREATE_FAILED',
        IN_PROGRESS: 'CREATE_IN_PROGRESS',

    }

StackStatuses = _StackStatuses()