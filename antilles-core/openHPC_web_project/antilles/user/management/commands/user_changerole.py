# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import sys

from django.core.management.base import BaseCommand

from antilles.user.models import User

from ._util import get_operator, print_green, print_red


class Command(BaseCommand):
    help = "change user's role."

    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            '--username',
            required=True,
            help='user name'
        )
        parser.add_argument(
            '-r',
            '--role',
            required=True,
            choices=['user', 'operator', 'admin'],
            help='user role'
        )

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        operator = get_operator()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print_red('The user {0} does not exist.'.format(username))
            sys.exit(1)

        if User.ROLES[role] != user.role:
            user.role = User.ROLES[role]
            user.save()

        print_green('change role to {0} finished for user {1}.'
                    .format(role, username))

        from antilles.optlog.optlog import EventLog
        EventLog.opt_create(
            operator, EventLog.user, EventLog.update,
            EventLog.make_list(user.id, username)
        )
