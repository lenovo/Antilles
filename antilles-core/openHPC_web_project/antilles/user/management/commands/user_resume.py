# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from antilles.user.models import User

from ._util import get_operator, print_green

__all__ = ['Command']


class Command(BaseCommand):
    help = 'resume user'

    def add_arguments(self, parser):
        parser.add_argument(
            metavar='username', dest='username', help='user name'
        )

    def handle(self, *args, **options):
        operator = get_operator()
        from antilles.optlog.optlog import EventLog
        username = options['username']
        user = User.objects.get(username=username)
        user.effective_time = now()
        user.fail_chances = 0
        user.save()

        EventLog.opt_create(
            operator, EventLog.user, EventLog.update,
            EventLog.make_list(user.id, username)
        )
        print_green('User {} unfreeze success.'.format(username))
