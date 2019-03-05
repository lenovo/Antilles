# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from os import path

from django.conf import settings
from django.core.checks import Error, Tags, register
from django.core.management.base import BaseCommand

__all__ = ['Command']


@register(Tags.compatibility)
def check_db_connection(app_configs, **kwargs):
    from django.db.utils import OperationalError
    from django.db import connections

    errors = []
    for key in connections.databases.keys():
        try:
            connections[key].cursor()
        except OperationalError:
            errors.append(
                Error(
                    'Could connect to db.',
                    hint='Please check your database configure.',
                    obj=key,
                    id='antilles.common.E001'
                )
            )
    return errors


@register(Tags.compatibility)
def check_rabbitmq_connection(app_configs, **kwargs):
    errors = []
    import pika
    from pika.exceptions import AMQPConnectionError

    try:
        pika.BlockingConnection(
            pika.URLParameters(
                settings.BROKER_URL
            )
        )
    except AMQPConnectionError:
        errors.append(
            Error(
                'Could connect to rabbitmq.',
                hint='Please check your rabbitmq configure.',
                obj=settings.BROKER_URL,
                id='antilles.common.E003'
            )
        )

    return errors


def _check_dir(prop, id):
    errors = []
    directory = getattr(settings, prop)
    if not path.isdir(directory):
        errors.append(
            Error(
                'directory is not exists.',
                hint='Please create directory',
                obj=directory,
                id=id,
            )
        )
    return errors


@register(Tags.compatibility)
def check_log_dir(app_configs, **kwargs):
    return _check_dir('LOG_DIR', 'antilles.common.E004')


@register(Tags.compatibility)
def check_download_dir(app_configs, **kwargs):
    return _check_dir('DOWNLOAD_DIR', 'antilles.common.E005')


@register(Tags.compatibility)
def check_upload_dir(app_configs, **kwargs):
    return _check_dir('UPLOAD_DIR', 'antilles.common.E006')


@register(Tags.compatibility)
def check_lock_dir(app_configs, **kwargs):
    return _check_dir('LOCK_DIR', 'antilles.common.E006')


@register(Tags.compatibility)
def check_alarm_agent_reachable(app_configs, **kwargs):
    from antilles.alarm import check
    return check.check_alarm_agent()


def cleanNodesSensitiveContent(configure_file):
    if path.exists(configure_file):
        with open(configure_file, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            ipmi_user_idx = 0
            ipmi_pwd_idx = 0
            for line in lines:
                if ipmi_user_idx > 0 and ipmi_pwd_idx > 0 \
                        and line.find(',') >= 0:
                    cells = line.split(',')
                    if len(cells[ipmi_user_idx]) > 0:
                        cells[ipmi_user_idx] = '******'
                    if len(cells[ipmi_pwd_idx]) > 0:
                        cells[ipmi_pwd_idx] = '******'
                    f.write(','.join(cells))
                else:
                    f.write(line)
                    # locate the nodes section
                    if line.startswith('node') and line.find(',') >= 0:
                        columns = line.split(',')
                        for idx in range(len(columns)):
                            if columns[idx] == 'ipmi_user':
                                ipmi_user_idx = idx
                            if columns[idx] == 'ipmi_pwd':
                                ipmi_pwd_idx = idx


class Command(BaseCommand):
    help = 'start antilles'

    def add_arguments(self, parser):
        parser.add_argument(
            '-n', '--nodaemon', action="store_true",
            default=False,
            help='Run in the foreground'
        )

        parser.add_argument(
            '--concurrency', default='4',
            help='Number of child processes processing the queue'
        )

    def sync_node(self):
        if settings.AUTO_SYNC_NODES:
            from antilles.cluster.utils import config, sync

            conf = config.Configure.parse(
                settings.NODES_FILE
            )
            sync.sync2db(configure=conf)
            sync.sync2confluent(configure=conf)
            cleanNodesSensitiveContent(configure_file=settings.NODES_FILE)

    def init_rabbitmq(self):
        import pika
        with pika.BlockingConnection(
                pika.URLParameters(
                    settings.BROKER_URL
                )
        ) as connection:
            channel = connection.channel()

            channel.exchange_declare(exchange="openhpc", exchange_type="topic")

            channel.queue_declare(queue="job", durable=True)
            channel.queue_purge(queue="job")
            channel.queue_bind(
                exchange="openhpc", queue="job", routing_key="job"
            )

            channel.queue_declare(queue="ai", durable=True)
            channel.queue_purge(queue="ai")
            channel.queue_bind(
                exchange="openhpc", queue="ai", routing_key="ai"
            )

    def start_server(self, **options):
        from supervisor import supervisord
        args = ['-c', '/etc/antilles/supervisord.conf']
        if options['nodaemon']:
            args.append('--nodaemon')

        supervisord.main(args)

    def clear_import_record(self, **options):
        from antilles.user.models import ImportRecord
        ImportRecord.objects.all().update(task_id='')

    def handle(self, *args, **options):
        self.sync_node()
        self.init_rabbitmq()
        self.clear_import_record()
        self.start_server(**options)
