# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from getpass import getpass

from django.core.management.base import BaseCommand
from six import print_

from antilles.user.models import LibuserConfig


class Command(BaseCommand):
    help = "Set openldap admin password."

    def handle(self, *args, **options):
        password = getpass('Please input your ldap password: ')
        confirm = getpass('Please confirm the ldap password: ')

        if password != confirm:
            print_('The ldap passwords entered did not match.')
            exit(1)
        else:
            LibuserConfig.objects.update_or_create(
                key='ldap/password',
                defaults={
                    'value': password
                }
            )
