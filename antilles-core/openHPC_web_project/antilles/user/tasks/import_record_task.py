# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import fcntl
import os
import pwd
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from antilles.user.models import BillGroup, ImportRecord, User

logger = get_task_logger(__name__)


IMPORT_LOCK_FILE = "import_record.lock"


def check_task_id_valid(username):
    retry = 3
    while retry > 0:
        records = ImportRecord.objects.filter(
            action_username=username
        )
        if records.count() == 0:
            logger.info("No user record can be imported.")
            return False

        task_id = records[0].task_id
        if task_id:
            return True

        retry -= 1
        time.sleep(1)
    return False


def update_users(action_username):
    valid = check_task_id_valid(action_username)
    if not valid:
        logger.error("Import record task id do not updated in db.")
        return

    try:
        records = ImportRecord.objects.filter(
            action_username=action_username
        ).order_by('row')
        for record in records:
            try:
                pwd.getpwnam(record.username)
            except KeyError:
                record.status = 'error'
                record.error_message = 'The user does not exist'
                record.save()
                continue

            if len(BillGroup.objects.filter(
                name=record.bill_group_name
            )) == 0:
                record.status = 'error'
                record.error_message = 'The bill group dose not exist'
                record.save()
                continue

            User.objects.update_or_create(
                username=record.username,
                defaults={
                    "first_name": record.first_name,
                    "last_name": record.last_name,
                    "email": record.email,
                    "role": record.role,
                    "bill_group": BillGroup.objects.get(
                        name=record.bill_group_name
                    )
                }
            )
            record.status = 'success'
            record.save()

    except Exception:
        logger.exception("Import record failed.")
        raise
    finally:
        ImportRecord.objects.all().update(task_id='')


@shared_task(time_limit=3600)
def import_record(action_username, get_lock_time_limit=60):

    # request will release the file lock, task should handle
    # the file lock again
    lock_dir = settings.LOCK_DIR
    lock_file = os.path.join(lock_dir, IMPORT_LOCK_FILE)

    file_locked = True

    with open(lock_file, 'w') as fd:
        while file_locked and get_lock_time_limit > 0:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except Exception:
                logger.exception("Lock file has been occupied.")
                get_lock_time_limit -= 1

                import time
                time.sleep(1)

                continue
            file_locked = False

        if file_locked:
            logger.error("Import record task cannot get the file lock")
            return

        update_users(action_username)
