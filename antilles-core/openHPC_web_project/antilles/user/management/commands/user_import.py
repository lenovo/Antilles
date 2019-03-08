# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import csv
import fcntl
import os
import pwd
import sys

from django.conf import settings
from django.core.management import BaseCommand

from antilles.user.managers.user import UsermanagerException, usermanager
from antilles.user.models import BillGroup, Deposit, User
from antilles.user.permissions import USER_ROLES

from ._util import get_operator, print_green, print_red

IMPORT_LOCK_FILE = "import_record.lock"
TITLES = (
    "username",
    "role",
    "last_name",
    "first_name",
    "bill_group_name",
    "email"
)
ROLES = {r[1]: r[0] for r in USER_ROLES}


class Command(BaseCommand):
    help = 'import user(s) from nss to db.'

    def add_arguments(self, parser):

        import_group = parser.add_argument_group('Import User')
        import_group.add_argument(
            '-u', '--username', required=False,
            help='user name'
        )
        import_group.add_argument(
            '-b', '--bill_group', help='bill group name',
            default=settings.DEFAULT_BILL_GROUP
        )
        import_group.add_argument(
            '-r', '--role', default='user',
            choices=['user', 'operator', 'admin'], help='user role'
        )
        import_group.add_argument(
            '-c', '--credits', type=int,
            help='the credits deposited for the billgroup',
            default=settings.DEFAULT_CREDITS
        )

        batch_import_group = parser.add_argument_group('Batch Import User')
        batch_import_group.add_argument(
            '-f', '--filename', required=False,
            help='batch import users from csv file'
        )

    def handle(self, *args, **options):

        if not options["username"] and not options["filename"]:
            print_red("one of the arguments --username --filename is required")
            sys.exit(1)

        if options["filename"]:
            mutually_exclusive_options = (
                "username",
                # "bill_group",
                # "role",
                # "credits"
            )
            for me_option in mutually_exclusive_options:
                if options[me_option]:
                    print_red("argument --filename: not allowed "
                              "with argument --{0}".format(me_option))
                    sys.exit(1)

            self._batch_import_user(options)
        else:
            self._import_user(options)

        print_green("Import user finished")

    @staticmethod
    def _check_user(username):
        try:
            pwd.getpwnam(username)
        except KeyError:
            print_red(
                'Error: the user {0} does not exist in nss'.format(username))
            sys.exit(1)

    def _import_user(self, options):
        operator = get_operator()
        self._check_user(options['username'])
        try:
            billgroup = BillGroup.objects.update_or_create(
                name=options['bill_group'],
                defaults=dict(balance=options['credits'], )
            )[0]
            manager = usermanager.as_operator(operator)
            manager.import_user(
                options['username'],
                billgroup,
                role=options['role'],
            )
            Deposit.objects.get_or_create(
                credits=options['credits'],
                user=User.objects.get(username=options['username']),
                bill_group=billgroup
            )
        except UsermanagerException as e:
            print_red(e)
            sys.exit(1)

    def _batch_import_user(self, options):

        lock_dir = settings.LOCK_DIR
        lock_file = os.path.join(lock_dir, IMPORT_LOCK_FILE)
        if not os.path.exists(lock_file):
            os.mknod(lock_file)

        with open(lock_file, 'w') as fd:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except Exception as e:
                # print_red(e)
                print_red("Batch import user records process is occupied")
                sys.exit(1)

            fname = options['filename']
            users = self._validate_csv_file(self, fname)

            print("The users in csv file is importing ...")
            try:
                for username, user in users.items():
                    User.objects.update_or_create(
                        username=username,
                        defaults=user
                    )

            except Exception as e:
                print_red("Import failed: {0}".format(e))
                sys.exit(1)

    @staticmethod
    def _check_batch_user(line_no, username, users):
        if username in users:
            print_red("Username duplicated: {0}"
                      " - Line{1}".format(username, line_no))
            sys.exit(1)

        try:
            pwd.getpwnam(username)
        except KeyError:
            print_red("user {0} does not exist in nss"
                      " - Line{1}".format(username, line_no))
            sys.exit(1)

    @staticmethod
    def _check_batch_group(line_no, bill_group_name):
        if not bill_group_name:
            print_red("Billgroup name cannot be empty"
                      " - Line{0}".format(line_no))
            sys.exit(1)

        if len(BillGroup.objects.filter(name=bill_group_name)) == 0:
            print_red("The bill group dose not exist: {0}"
                      " - Line{1}".format(bill_group_name, line_no))
            sys.exit(1)

    @staticmethod
    def _check_batch_role(line_no, user_role):
        if user_role not in ROLES.keys():
            print_red("User role is invalid - Line{0}".format(line_no))
            sys.exit(1)

    @staticmethod
    def _validate_csv_file(self, filename):
        # check file content
        users = {}
        with open(filename) as record_csv:
            try:
                reader = csv.DictReader(record_csv)

                titles = reader.fieldnames
                t = [title.strip().lower() for title in titles]

                if len(titles) != len(TITLES) or not set(t) == set(TITLES):
                    print_red("The titles in csv file is invalid")
                    sys.exit(1)

                for i, row in enumerate(reader):
                    line_no = i + 1
                    row = {k.strip().lower(): v.strip()
                           for k, v in row.items() if v and v.strip()}
                    if not row:
                        continue

                    # check username
                    username = row["username"]
                    self._check_batch_user(line_no, username, users)

                    # check billgroup
                    bill_group_name = row["bill_group_name"]
                    self._check_batch_group(line_no, bill_group_name)

                    # check user role
                    user_role = row["role"].lower()
                    self._check_batch_role(line_no, user_role)

                    row["role"] = ROLES[user_role]
                    row["bill_group"] = BillGroup.objects.get(
                        name=bill_group_name
                    )
                    row.pop("bill_group_name")

                    # delete empty fields
                    [row.pop(k) for k, v in row.items() if not v]

                    users[username] = row
            except Exception as e:
                print_red(e)
                print_red("The format of file is invalid")
                sys.exit(1)

            return users
