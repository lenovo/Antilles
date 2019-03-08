# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.core.management.base import BaseCommand

__all__ = ['Command']


class Command(BaseCommand):
    help = 'show antilles status'

    def handle(self, *args, **options):
        from supervisor import supervisorctl
        supervisorctl.main([
            '-c', '/etc/antilles/supervisord.conf', 'status'
        ])
