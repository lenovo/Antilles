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
    help = 'launch alarm creator worker.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--log-level', default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL'],
            help='Logging level'
        )

    def handle(self, *args, **options):
        app = Celery(__name__)
        app.config_from_object('django.conf:settings')
        from antilles.alarm.scanner.creator_tasks import create_alarm
        app.conf.task_default_queue = "create_alarm"
        app.task(create_alarm)

        app.start(
            argv=['celery', 'worker', '-l', options['log_level'], '-P', 'solo']
        )
