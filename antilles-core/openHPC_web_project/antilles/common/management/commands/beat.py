# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from celery import Celery
from django.core.management.base import BaseCommand

__all__ = ['Command']


class Command(BaseCommand):
    help = 'launch celery beat.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--log-level', default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL'],
            help='Logging level'
        )
        parser.add_argument(
            '--conf-path', default='/var/run/antilles/core',
            help='Store pid file and schedule db'
        )

    def handle(self, *args, **options):
        app = Celery(__name__)
        app.config_from_object('django.conf:settings')

        celery_conf_path = options['conf_path']
        from os import makedirs, path
        if not path.exists(celery_conf_path):
            makedirs(celery_conf_path, mode=0755)

        pid_file = path.join(celery_conf_path, "celerybeat.pid")
        schedule_db = path.join(celery_conf_path, "celerybeat-schedule")

        app.start(
            argv=['celery', 'beat', '-l', options['log_level'],
                  '--pidfile', pid_file, '-s', schedule_db]
        )
