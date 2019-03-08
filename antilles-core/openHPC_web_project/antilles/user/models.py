# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from __future__ import unicode_literals

import grp
import pwd
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import (
    BigIntegerField, CharField, DateTimeField, EmailField, FloatField,
    ForeignKey, IntegerField, Model, TextField,
)
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from .permissions import ROLE_ADMIN, USER_ROLES


def grp_to_dict(group):
    return {
        'gid': group.gr_gid,
        'name': group.gr_name,
        'password': group.gr_passwd,
        'members': group.gr_mem
    }


class Deposit(models.Model):
    # XXX delete when user delete
    user = ForeignKey('User', null=True, on_delete=models.CASCADE,
                      db_column='user')
    # XXX delete when bill_group delete
    bill_group = ForeignKey('BillGroup', null=True, on_delete=models.CASCADE,
                            db_column='bill_group')
    credits = models.FloatField(default=0)
    apply_time = models.DateTimeField(null=True)
    approved_time = models.DateTimeField(null=True)

    def as_dict(self, **karg):
        data = model_to_dict(self,
                             fields=karg.get('fields', []),
                             exclude=karg.get('exclude', []))
        data['user'] = self.user.username
        # data['bill_group'] = self.bill_group.name
        if self.bill_group:
            data['bill_group'] = model_to_dict(self.bill_group,
                                               fields=[],
                                               exclude=[])
        return data


class BillGroup(Model):
    name = CharField(null=False, default="default_bill_group",
                     max_length=20, unique=True)
    balance = FloatField(null=False, default=0)
    charged = FloatField(null=False, default=0)
    used_time = BigIntegerField(null=False, default=0)
    used_credits = FloatField(null=False, default=0)
    description = CharField(null=False, default="",
                            blank=True, max_length=200)
    charge_rate = FloatField(null=False, default=1)
    last_operation_time = DateTimeField(null=True)

    def as_dict(self, **karg):
        default_fields = []
        default_exclude = []
        fields = karg.get('fields', default_fields)
        exclude = karg.get('exclude', default_exclude)
        data = model_to_dict(self, fields=fields, exclude=exclude)
        return data


class User(Model):
    ROLES = {r[1]: r[0] for r in USER_ROLES}

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    username = CharField(
        unique=True, max_length=32,
        error_messages={'username': "User already exists"}
    )
    first_name = CharField(max_length=30, null=True)
    last_name = CharField(max_length=30, null=True)

    email = EmailField(null=True)
    role = IntegerField(choices=USER_ROLES, default=USER_ROLES[-1][0])

    last_login = DateTimeField(null=True)
    date_joined = DateTimeField(default=timezone.now)
    last_operation_time = DateTimeField(null=True)

    bill_group = ForeignKey('BillGroup', null=True,
                            related_name="bill_members",
                            on_delete=models.PROTECT)

    fail_chances = IntegerField(default=0, null=False)
    effective_time = DateTimeField(auto_now_add=True, null=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        try:
            self._passwd = pwd.getpwnam(self.username)
        except KeyError:
            self._passwd = None

    def login_success(self):
        self.last_login = timezone.now()
        self.fail_chances = 0
        self.save()

    def login_fail(self):
        self.fail_chances += 1
        if self.fail_chances >= settings.LOGIN_FAIL_MAX_CHANCE:
            self.fail_chances = 0
            self.effective_time = \
                timezone.now() + settings.LOGIN_FAIL_LOCKED_DURATION

        self.save()

    @property
    def remain_chances(self):
        return settings.LOGIN_FAIL_MAX_CHANCE - self.fail_chances

    @property
    def remain_time(self):
        now = timezone.now()
        return timedelta() \
            if now >= self.effective_time \
            else self.effective_time-now

    def is_activate(self):
        return timezone.now() >= self.effective_time

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.role >= ROLE_ADMIN

    @property
    def workspace(self):
        return self._passwd.pw_dir if self._passwd else None

    @property
    def uid(self):
        return self._passwd.pw_uid if self._passwd else None

    @property
    def gid(self):
        return self._passwd.pw_gid if self._passwd else None

    @property
    def group(self):
        if self._passwd is not None:
            try:
                return grp.getgrgid(self._passwd.pw_gid)
            except KeyError:
                return None
        else:
            return None

    @classmethod
    def get_role_value(cls, role):
        return cls.ROLES[role]

    @property
    def freeze_time(self):
        import time
        return time.mktime(
            self.effective_time.timetuple()) if not \
            self.is_activate() else None

    def as_dict(self, **karg):
        data = model_to_dict(self)
        data.update(
            role=self.get_role_display(),
            workspace=self.workspace,
            is_freezed=not self.is_activate(),
            effective_time=self.freeze_time
        )

        data['bill_group'] = model_to_dict(
            self.bill_group,
        ) if self.bill_group else None

        data['os_group'] = grp_to_dict(self.group) if self.group else None

        return data

    def require_role(self, cls):
        if self.role < cls.floor:
            raise PermissionDenied

    def check_role(self, role):
        floor = self.ROLES.get(role, 0)
        return self.role >= floor


class LibuserConfig(Model):
    key = TextField(primary_key=True, null=False)
    value = TextField(null=False)


class ImportRecord(Model):
    ROLES = {r[1]: r[0] for r in USER_ROLES}

    row = IntegerField(null=False)
    action_username = CharField(max_length=32, null=False)
    task_id = CharField(max_length=40, null=True)
    username = CharField(max_length=32, null=False)
    role = IntegerField(choices=USER_ROLES, default=USER_ROLES[-1][0])
    first_name = CharField(max_length=30, null=True)
    last_name = CharField(max_length=30, null=True)
    bill_group_name = CharField(max_length=20, null=False)
    email = EmailField(null=True)
    status = CharField(max_length=24, null=True)
    error_message = CharField(max_length=50, null=True)

    create_time = DateTimeField(auto_now_add=True)
    update_time = DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ("action_username", "row"),
            ("action_username", "username")
        )

    @classmethod
    def get_role_value(cls, role):
        return cls.ROLES[role]

    def as_dict(self, **karg):
        data = model_to_dict(
            self,
            fields=karg.get('fields', []),
            exclude=karg.get('exclude', [])
        )
        data.update(role=self.get_role_display())

        return data


class Preference(Model):
    name = CharField(max_length=256)
    value = TextField(null=False)
    user = ForeignKey(User, null=True, on_delete=models.CASCADE,
                      help_text=b'null:scope is global,'
                                b'otherwise scope is local')
    create_time = DateTimeField(auto_now_add=True)
    modify_time = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'user')
