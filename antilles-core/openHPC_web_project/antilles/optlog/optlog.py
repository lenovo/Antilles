# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from antilles.optlog.models import LogDetail, OperationLog

logger = logging.getLogger(__name__)


class EventLog(object):
    user = OperationLog.USER
    job = OperationLog.JOB
    node = OperationLog.NODE
    alarm = OperationLog.ALARM
    policy = OperationLog.POLICY
    billgroup = OperationLog.BILLGROUP
    deposit = OperationLog.DEPOSIT
    osgroup = OperationLog.OSGROUP
    create = OperationLog.CREATE
    update = OperationLog.UPDATE
    delete = OperationLog.DELETE
    recharge = OperationLog.RECHARGE
    chargeback = OperationLog.CHARGEBACK
    confirm = OperationLog.CONFIRM
    solve = OperationLog.SOLVE
    turn_on = OperationLog.TURN_ON
    turn_off = OperationLog.TURN_OFF
    cancel = OperationLog.CANCEL
    rerun = OperationLog.RERUN
    comment = OperationLog.COMMENT

    @classmethod
    def opt_create_instance(cls, target, **kwargs):
        def create(args):
            try:
                LogDetail.objects.create(
                    object_id=args[0], optlog=optobj, name=args[1]
                )
            except Exception as e:
                logging.warn(e.message, exc_info=True)

        try:
            optobj = OperationLog.objects.create(**kwargs)
            map(create, target)
        except Exception as e:
            logging.warn(e.message, exc_info=True)

    @classmethod
    def opt_create(cls, operator, module, operation, target):
        data = {
            'operator': operator,
            'module': module,
            'operation': operation,
        }

        cls.opt_create_instance(target, **data)

    @classmethod
    def make_list(cls, id, name):
        return [(id, name)]
