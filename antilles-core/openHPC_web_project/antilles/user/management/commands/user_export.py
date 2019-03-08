# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import csv
import os

from django.core.management.base import BaseCommand

from antilles.user.models import User
from antilles.user.permissions import USER_ROLES


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '-f',
            '--filename',
            required=True,
            help='the FILENAME is the name of the file that will be exported'
        )

    def handle(self, *args, **options):

        titles = [
            'username',
            'role',
            'last_name',
            'first_name',
            'bill_group',
            'email',
            'is_active'
        ]
        roles = {r[0]: r[1] for r in USER_ROLES}

        filename = options['filename']
        path = os.path.join(os.getcwd(), filename)

        with open(path, "w") as f:
            writer = csv.writer(f, delimiter=b',', lineterminator='\r\n')
            writer.writerow(titles)

            users = User.objects.iterator()

            for user in users:
                writer.writerow([
                    user.username,
                    roles[user.role],
                    user.last_name,
                    user.first_name,
                    user.bill_group.name,
                    user.email,
                    user.is_activate()
                ])
