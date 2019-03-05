# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from django.core.exceptions import ObjectDoesNotExist
from pytest import mark

from antilles.optlog.models import LogDetail, OperationLog
from antilles.optlog.optlog import EventLog


@mark.django_db
def test_optbase():
    EventLog.opt_create(
        'zhanghe', 'Alarm', 'Create',
        EventLog.make_list(1, 'antilles')
    )
    op = OperationLog.objects.all()
    log = LogDetail.objects.all()
    assert len(op) == 1
    assert op[0].operator == 'zhanghe'
    assert op[0].operation == 'Create'
    assert len(log) == 1
    assert log[0].name == 'antilles'
    assert log[0].id == 1


@mark.django_db
def test_optbase_already_exists(mocker):
    mocker.patch(
        'antilles.optlog.models.LogDetail.objects.create',
        side_effect=ObjectDoesNotExist('an exception')
    )

    EventLog.opt_create('zhanghe', 'Alarm', 'Create', [[1, 'antilles']])

    assert len(OperationLog.objects.all()) == 1
    assert len(LogDetail.objects.all()) == 0
