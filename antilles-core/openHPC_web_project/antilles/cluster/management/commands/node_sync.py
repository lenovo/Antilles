# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from django.core.management import BaseCommand

from antilles.cluster.utils import config, sync

__all__ = ["Command"]


def cleanNodesSensitiveContent(configure_file):
    from os import path
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
    help = 'sync node from nodes.csv'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)

        conf = config.Configure.parse(
            settings.NODES_FILE
        )
        sync.sync2db(configure=conf)
        sync.sync2confluent(configure=conf)
        cleanNodesSensitiveContent(configure_file=settings.NODES_FILE)
