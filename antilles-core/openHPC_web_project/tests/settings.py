# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from configurations import Configuration
from cryptography.fernet import Fernet
from pkg_resources import resource_filename


class Base(Configuration):
    DEBUG = True

    SECRET_KEY = Fernet.generate_key()

    DOMAIN = 'hpc.com'

    INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        'rest_framework',
        'antilles.optlog',
        'antilles.logs',
        'antilles.user',
        'antilles.alarm',
        'antilles.cluster',
        'antilles.scheduler',
        'django_celery_results'
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'debug': False
            },
        },
    ]

    MIDDLEWARE_CLASSES = ()

    LANGUAGE_CODE = 'en'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LANGUAGES = (
        ('en', 'English'),
        ('sc', 'Simplified Chinese'),
    )

    LOCALE_PATHS = (
        resource_filename('antilles_web', 'locale'),
    )

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s'
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }

    USER_BACKEND = 'libuser'
    ANTILLES_PAM_SERVICE = 'antilles'
    AUTHENTICATION_BACKENDS = ('antilles.user.plugins.AuthBackend',)

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'antilles.user.plugins.JWTAuthentication',
            'antilles.user.plugins.CookieAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'antilles.user.permissions.AsUserRole',
        ),
        'DEFAULT_VERSIONING_CLASS':
            'rest_framework.versioning.NamespaceVersioning',
        'EXCEPTION_HANDLER': 'antilles.common.plugins.exception_handler',
    }

    REQUESTS_TIMEOUT = 1

    MIN_UID = 1000

    BROKER_URL = "amqp://guest:guest@127.0.0.1:5672/"


class Standalone(Base):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }


class Jenkins(Base):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '127.0.0.1',
            'NAME': 'antilles',
            'USER': 'postgres',
            'PASSWORD': '123456'
        }
    }
