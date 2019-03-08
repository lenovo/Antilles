# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.db import models


class OperationLog(models.Model):
    USER = 'user'
    JOB = 'job'
    NODE = 'node'
    ALARM = 'alarm'
    POLICY = 'policy'
    BILLGROUP = 'billgroup'
    DEPOSIT = 'deposit'
    OSGROUP = 'osgroup'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    RECHARGE = 'recharge'
    CHARGEBACK = 'chargeback'
    CONFIRM = 'confirm'
    SOLVE = 'solve'
    TURN_ON = 'turn_on'
    TURN_OFF = 'turn_off'
    CANCEL = 'cancel'
    RERUN = 'rerun'
    COMMENT = 'comment'

    module = models.CharField(max_length=128, null=False, blank=False)
    operate_time = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=128, null=False, blank=False)
    operator = models.CharField(max_length=256, null=False, blank=False)


class LogDetail(models.Model):
    object_id = models.IntegerField()
    name = models.CharField(
        max_length=256, null=False, blank=False
    )
    optlog = models.ForeignKey(
        'OperationLog', related_name='target', on_delete=models.PROTECT
    )
