# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from __future__ import unicode_literals

import csv
import fcntl
import grp
import logging
import os
import pwd
import uuid

from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from antilles.common.utils import json_schema_validate
from antilles.common.views import DataTableView

from ..managers.user import UserManager
from ..managers.user.exceptions import RemoveLastAdminException
from ..models import ImportRecord, User, grp_to_dict
from ..permissions import USER_ROLES, AsAdminRole, AsOperatorRole, AsUserRole
from .exceptions import (
    BillgroupEmptyException, CannotCancelImportRecordProcessException,
    FileFormatInvalidException, ImportRecordProcessRunningException,
    NoImportRecordProcessRunningException, NoTaskIdException,
    TaskIdInsertFailException, TitleFieldsInvalidException,
    UserDuplicateException, UserEmptyException, UserRoleInvalidException,
)

logger = logging.getLogger(__name__)


usermanager = UserManager()
IMPORT_LOCK_FILE = "import_record.lock"


class UserListView(DataTableView):
    columns_mapping = {
        'bill_group': 'bill_group__name'
    }

    def trans_result(self, result):
        result = result.as_dict()
        return {
            'bill_group': {
                'name': result['bill_group']['name'] if
                result.get('bill_group', None) else None,
                'id': result['bill_group']['id']
                if result.get('bill_group', None) else None
            },
            'id': result.get('id', None),
            'username': result.get('username', None),
            'first_name': result.get('first_name', None),
            'last_name': result.get('last_name', None),
            'role': result.get('role', None),
            'is_freezed': result.get('is_freezed', None),
            'effective_time': result.get('effective_time', None),
            'last_login': result.get('last_login', None),
            'email': result.get('email', None),
        }

    def get_query(self, request, *args, **kwargs):
        return User.objects

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'os_group': {
                'type': 'string',
                'minLength': 1
            },
            'bill_group': {
                'type': 'integer',
                'minimum': 0
            },
            'username': {
                'type': 'string',
                'minLength': 1
            },
            'password': {
                'type': 'string',
                'minLength': 1
            },
            'role': {
                'enum': ['admin', 'operator', 'user']
            },
            'first_name': {
                'type': 'string'
            },
            'last_name': {
                'type': 'string'
            },
            'email': {
                'type': 'string',
            }
        },
        'required': [
            'bill_group',
            'os_group',
            'username',
            'password',
            'role',
        ]
    })
    @AsAdminRole
    def post(self, request):
        # do create
        user = usermanager \
            .as_operator(request.user.username) \
            .add_user(**request.data)

        return Response(user)


class UserDetailView(APIView):
    permission_classes = (AsAdminRole, )

    @AsUserRole
    def get(self, request, pk):
        # return Response(
        #     User.objects.get(id=pk).as_dict()
        # )
        user = usermanager.get_user(pk)
        return Response(user)

    def delete(self, request, pk):
        pk = int(pk)
        if usermanager.is_last_admin(pk):
            raise RemoveLastAdminException
        usermanager \
            .as_operator(request.user.username) \
            .remove_user(pk)
        return Response(status=204)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'role': {
                'enum': ['admin', 'operator', 'user']
            },
            'email': {
                'type': 'string',
            },
            'last_name': {
                'type': 'string'
            },
            'first_name': {
                'type': 'string'
            },
            'bill_group': {
                'type': 'integer',
                'minimum': 0
            },
            'os_group': {
                'type': 'string'
            },
        },
        'required': [
            'role',
            'bill_group'
        ]
    })
    def patch(self, request, pk):
        pk = int(pk)
        usermanager \
            .as_operator(request.user.username) \
            .update_user(pk, request.data)
        user = usermanager \
            .get_user(pk)

        return Response(user)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'username': {
                'type': 'string',
                'minLength': 1
            },
            'bill_group': {
                'type': 'integer',
                'minimum': 0
            },
            'role': {
                'enum': ['admin', 'operator', 'user']
            },
            'email': {
                'type': 'string',
            },
            'first_name': {
                'type': 'string',
            },
            'last_name': {
                'type': 'string',
            },
        },
        'required': [
            'username',
            'bill_group',
            'role',
        ]
    })
    def put(self, request, pk):
        data = request.data
        data['username'] = pk
        # verify param
        # getcallargs(usermanager.add_user, **request.data)
        username = usermanager \
            .as_operator(request.user.username) \
            . import_user(**data)['username']
        user = usermanager \
            .get_user(username)
        return Response(user)


class OSGroupListView(APIView):
    permission_classes = (AsAdminRole, )

    @AsOperatorRole
    def get(self, request):
        """
        list groups
        """
        groups = usermanager.get_all_groups()
        return Response(groups)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 1
            }
        },
        'required': [
            'name'
        ]
    })
    def post(self, request):
        '''creaet group'''
        groupname = request.data['name']
        usermanager \
            .as_operator(request.user.username) \
            .add_group(groupname)
        return Response({'name': groupname})


class OSGroupDetailView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request, pk):
        """
        get single group
        """
        try:
            group = grp.getgrnam(pk)
            return Response(grp_to_dict(group))
        except KeyError:
            raise NotFound

    def delete(self, request, pk):
        '''delete group'''
        usermanager \
            .as_operator(request.user.username) \
            .remove_group(pk)
        return Response(status=HTTP_204_NO_CONTENT)


class UnimportedUserListView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request):
        users = [u.pw_name for u in pwd.getpwall() if u.pw_uid >=
                 settings.MIN_UID]
        current_users = [u.username for u in User.objects.iterator()]
        users = filter(lambda u: u not in current_users, users)
        return Response(users)


class UserImportView(APIView):
    permission_classes = (AsAdminRole, )

    def task_ready(self, task_id):
        '''
        True  -> task finished
        False -> task running
        '''
        if not task_id:
            return True
        from celery import Celery
        app = Celery(__name__)
        app.config_from_object('django.conf:settings')

        from antilles.user.tasks import import_record
        task = import_record.AsyncResult(task_id)
        return task.ready()

    def get_import_process_status(self):
        '''
        get the import user process status, and process's owner
        True  -> running
        False -> not running
        return (<process_status>, <admin_name>)
        '''
        task_ids_set = ImportRecord.objects.values('task_id').distinct()
        for t in task_ids_set:
            if not self.task_ready(t["task_id"]):
                action_username = ImportRecord.objects.filter(
                    task_id=t["task_id"]
                )[0].action_username
                return True, action_username

        return False, None

    def validate_import_record_csv_title(self, titles, nessary_titles):
        for nessary_title in nessary_titles:
            if titles.count(nessary_title) > 1:
                return False, {"duplicate": nessary_title}
            elif titles.count(nessary_title) < 1:
                return False, {"lose": nessary_title}
            else:
                continue

        return True, {}

    def validate_import_record_csv(self, record_path):

        TITLES = (
            "username",
            "role",
            "last_name",
            "first_name",
            "bill_group_name",
            "email"
        )
        ROLES = {r[1]: r[0] for r in USER_ROLES}

        users = {}
        with open(record_path) as record_csv:
            try:
                reader = csv.DictReader(record_csv)
                titles = reader.fieldnames
            except Exception:
                raise FileFormatInvalidException

            t = [title.strip() for title in titles]

            ok, _ = self.validate_import_record_csv_title(t, TITLES)

            if not ok:
                raise TitleFieldsInvalidException

            for i, row in enumerate(reader):
                line_no = i + 1
                if not row["username"].strip():
                    raise UserEmptyException

                if row["username"].strip() in users:
                    raise UserDuplicateException

                if not row["bill_group_name"].strip():
                    raise BillgroupEmptyException

                user_role = row["role"].strip().lower()
                if user_role not in ROLES.keys():
                    raise UserRoleInvalidException

                row_data = {k.strip(): v.strip() for k, v in row.items()}

                user = {
                    "row": line_no,
                    "username": row_data["username"],
                    "role": ROLES[user_role],
                    "last_name": row_data["last_name"],
                    "first_name": row_data["first_name"],
                    "bill_group_name": row_data["bill_group_name"],
                    "email": row_data["email"]
                }

                # delete empty fields
                [user.pop(k) for k, v in user.items() if not v]

                users[row_data["username"].strip()] = user

            return users

    def get(self, request):
        status = "idle"
        current_user = request.user.username
        process_running, action_user = self.get_import_process_status()

        if process_running:
            if current_user != action_user:
                status = "occupied"
            else:
                status = "importing"

        # maybe user import command is running
        if status == "idle":
            lock_dir = settings.LOCK_DIR
            lock_file = os.path.join(lock_dir, IMPORT_LOCK_FILE)
            if os.path.exists(lock_file):
                with open(lock_file, 'w') as fd:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except Exception:
                        logger.exception(
                            "Import record lock file has been locked."
                        )
                        status = "occupied"

        records = ImportRecord.objects.filter(action_username=current_user)

        ret = {}
        ret["status"] = status

        if status != "importing":
            if records.count() == 0:
                return Response(ret)

            ret["last_importing"] = {
                "total": records.count(),
                "finished": records.filter(status__isnull=False).count(),
                "success": records.filter(status="success").count(),
                "finish_time": records.order_by(
                    "update_time"
                ).last().update_time
            }
        else:
            ret["progress"] = {
                "total": records.count(),
                "finished": records.filter(status__isnull=False).count(),
                "success": records.filter(status="success").count()
            }

        logger.debug("Get import record result: {0}".format(ret))

        return Response(ret)

    def post(self, request):
        current_user = request.user.username

        lock_dir = settings.LOCK_DIR
        # 1. check whether the import record process exist, file lock
        #    yes=>return; no=>continue
        lock_file = os.path.join(lock_dir, IMPORT_LOCK_FILE)
        if not os.path.exists(lock_file):
            os.mknod(lock_file)

        with open(lock_file, 'w') as fd:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except Exception as e:
                logger.exception(e)
                raise ImportRecordProcessRunningException

            # 2. get upload file import_user.csv
            #    handle fname, delete the file until all operation complete
            up_file = request.FILES.get('upload')

            upload_dir = settings.UPLOAD_DIR
            rename_upload_filename = "{0}_{1}.csv".format(
                os.path.splitext(up_file.name)[0], uuid.uuid1()
            )
            record_path = os.path.join(upload_dir, rename_upload_filename)
            with open(record_path, 'wb+') as f:
                for chunk in up_file.chunks():
                    f.write(chunk)

            # 3. validate user data in csv
            #    failed=>raise err; ok=> continue
            users = self.validate_import_record_csv(record_path)

            # 4. clear current user's last user_import_record
            # 5. import user record into table user_import_record
            ImportRecord.objects.filter(action_username=current_user).delete()
            for user in users.values():
                user["action_username"] = current_user
                ImportRecord.objects.create(**user)
                logger.info("Import user: {0}".format(user))

            #  ** after saved data into table, start the import record process
            from celery import Celery
            app = Celery(__name__)
            app.config_from_object('django.conf:settings')

            from antilles.user.tasks import import_record
            task = import_record.delay(current_user)

            try:
                ImportRecord.objects.filter(
                    action_username=current_user
                ).update(task_id=task.id)
            except Exception:
                logger.exception("Cannot update task_id into ImportRecord.")
                raise TaskIdInsertFailException

        return Response(status=HTTP_200_OK)

    def delete(self, request):
        current_user = request.user.username
        lock_dir = settings.LOCK_DIR
        lock_file = os.path.join(lock_dir, IMPORT_LOCK_FILE)

        tasks = ImportRecord.objects.filter(action_username=current_user)
        if tasks.count == 0:
            logger.info("Tasks count is 0.")
            raise NoImportRecordProcessRunningException

        task_id = tasks[0].task_id
        if not task_id:
            raise NoTaskIdException

        task_ready = False
        retry_chance = 3
        while retry_chance > 0 and not task_ready:
            import time
            time.sleep(2)

            retry_chance -= 1
            try:
                from celery.task.control import revoke

                revoke(task_id, terminate=True)
                task_ready = self.task_ready(task_id)

                if not task_ready:
                    continue
                logger.info("Import record Task {0} is cancelled".format(
                    task_id
                ))

                # clear db
                ImportRecord.objects.all().update(task_id='')

                # clear lock file
                if os.path.exists(lock_file):
                    os.remove(lock_file)
                return Response(status=HTTP_200_OK)
            except Exception as e:
                logger.exception(e)
                continue
        raise CannotCancelImportRecordProcessException


class UserImportDetailView(DataTableView):
    permission_classes = (AsAdminRole, )

    columns_mapping = {
        'row': 'row',
        'username': 'username',
        'role': 'role',
        'last_name': 'last_name',
        'first_name': 'first_name',
        'bill_group': 'bill_group_name',
        'email': 'email',
        'status': 'status',
    }

    def trans_result(self, result):
        result = result.as_dict()
        return {
            'row': result.get('row'),
            'username': result.get('username'),
            'role': result.get('role'),
            'last_name': result.get('last_name', ''),
            'first_name': result.get('first_name', ''),
            'bill_group': result.get('bill_group_name'),
            'email': result.get('email', ''),
            'status': result.get('status', ''),
            'error_message': result.get('error_message', ''),
        }

    def get_query(self, request, *args, **kwargs):
        return ImportRecord.objects.filter(
            action_username=request.user.username
        ).order_by('row')


class UserExportView(APIView):
    permission_classes = (AsAdminRole, )

    def post(self, request):
        export_file_name = "export_user_{0}.csv".format(uuid.uuid1())
        target = os.path.join(settings.DOWNLOAD_DIR, export_file_name)

        titles = [
            'username',
            'role',
            'last_name',
            'first_name',
            'bill_group_name',
            'email',
            'is_active'
        ]
        roles = {r[0]: r[1] for r in USER_ROLES}

        with open(target, "w") as f:
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

        return Response(
            data={'data': os.path.basename(target)}
        )
