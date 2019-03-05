# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

__all__ = ['Command']


class Command(BaseCommand):
    help = 'upgrade antilles'

    def handle(self, *args, **options):
        from django.core.management import call_command

        if raw_input('Have you already backup your database? (y/n) ') == 'y':
            call_command('migrate')
            call_command('user_init')
