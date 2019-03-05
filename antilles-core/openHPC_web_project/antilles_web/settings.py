# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import sys
from datetime import timedelta

from cryptography.fernet import Fernet
from pkg_resources import resource_filename

reload(sys)
sys.setdefaultencoding('utf-8')

SECRET_KEY = Fernet.generate_key()

MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = 'antilles_web.urls'

WSGI_APPLICATION = 'antilles_web.wsgi.application'

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', 'English'),
    ('sc', 'Simplified Chinese'),
)

LOCALE_PATHS = (
    resource_filename(__name__, 'locale'),
)

LOGGING_CONFIG = None

TOKEN_ALGORITHMS = 'HS512'
TOKEN_EXPIRE = timedelta(hours=1)

LOGIN_FAIL_LOCKED_DURATION = timedelta(hours=1)

ANTILLES_PAM_SERVICE = 'antilles'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'antilles.user.plugins.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'antilles.user.permissions.AsUserRole',
    ),
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.NamespaceVersioning',
    'EXCEPTION_HANDLER': 'antilles.common.plugins.exception_handler',
}

AUTHENTICATION_BACKENDS = (
    'antilles.user.plugins.AuthBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False
        },
    },
]

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json', 'yaml']
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_BACKEND = 'django-db'

CELERYD_TASK_TIME_LIMIT = 60
CELERYD_PREFETCH_MULTIPLIER = 1

CELERYBEAT_SCHEDULE = {
    'alarm-cpu-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.cpu_scanner',
        'schedule': 15
    },
    'alarm-disk-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.disk_scanner',
        'schedule': 15
    },
    'alarm-energy-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.energy_scanner',
        'schedule': 15
    },
    'alarm-temp-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.temp_scanner',
        'schedule': 15
    },
    'alarm-hardware-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.hardware_scanner',
        'schedule': 15
    },
    'alarm-node-active-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.node_active',
        'schedule': 15
    },
    'alarm-gpu-util-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.gpu_util_scanner',
        'schedule': 15
    },
    'alarm-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.gpu_temp_scanner',
        'schedule': 15
    },
    'alarm-gpu-temp-scanner': {
        'task': 'antilles.alarm.tasks.scanner_tasks.gpu_mem_scanner',
        'schedule': 15
    },
    'influx-running-job': {
        'task': 'antilles.cluster.tasks.job.running_job',
        'schedule': 15
    },
    'influx-group-summary': {
        'task': 'antilles.cluster.tasks.summary.group_summaries',
        'schedule': 15
    },
    'influx-rack-summary': {
        'task': 'antilles.cluster.tasks.summary.rack_summaries',
        'schedule': 15
    },
    'influx-cluster-summary': {
        'task': 'antilles.cluster.tasks.summary.cluster_summaries',
        'schedule': 15
    },
    'influx_node': {
        'task': 'antilles.cluster.tasks.node_summary.node_summaries',
        'schedule': 15
    },
    'influx_gpu': {
        'task': 'antilles.cluster.tasks.node_summary.node_gpu_summaries',
        'schedule': 15
    },
    'influx-cluster-monitor': {
        'task': 'antilles.cluster.tasks.summary.disk_summaries',
        'schedule': 30
    },
    'influx-cluster-schedule-monitor': {
        'task': 'antilles.scheduler.tasks.schedule_summaries',
        'schedule': 30
    },
}

CACHES = {
    'default': {
        'BACKEND': 'antilles.common.cache.Cache',
    }
}
