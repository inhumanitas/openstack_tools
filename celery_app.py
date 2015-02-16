# coding: utf-8

from __future__ import absolute_import

from celery import Celery

celery_app = Celery(
    'tasks',
    broker='amqp://guest@localhost//'
)

celery_app.conf.update(
    BROKER_URL='amqp://',
    CELERY_RESULT_BACKEND='amqp://',
    # CELERY_TASK_SERIALIZER='pickle',
    CELERY_IMPORTS=('tasks', ),
    CELERYD_CHDIR="/home/morose/work/git/openstack_tools/"
)
