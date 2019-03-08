# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from datetime import timedelta

from pytest import fixture

from antilles.alarm.models import Alarm, Policy
from antilles.optlog.models import OperationLog
from antilles.scheduler.models import Job
from antilles.user.models import BillGroup, User


@fixture(autouse=True)
def settings(settings, tmpdir):
    settings.ROOT_URLCONF = 'antilles.report.urls'
    return settings


def status():
    return [{'status': Alarm.PRESENT},
            {'status': Alarm.PRESENT},
            {'status': Alarm.CONFIRMED},
            {'status': Alarm.CONFIRMED}]


@fixture
def start_time():
    return 1525104000


@fixture
def end_time():
    return 5525967999


@fixture
def timezone_offset():
    return -480


@fixture
def data():
    return {
        'start_time': start_time(),
        'end_time': end_time(),
        'timezone_offset': timezone_offset(),
        'creator': 'hpcadmin',
        'language': 'sc',
        'page_direction': 'landscape',
    }


@fixture
def job():
    Job.objects.create(
        billgroup='default_bill_group',
        submiter='user_name',
        jobid='job_id',
        jobname='job_name',
        jobstatus='q',
        queue='q',
        qtime=1525104010,
        starttime=start_time(),
        endtime=end_time(),
        cpuscount=10,
        charge=6,
        gpuscount=2,
        gpucharge=2
    )


@fixture
def user():
    User(
        username='user_name'
    ).save()


@fixture
def policy():
    for i, s in enumerate(status()):
        p = Policy.objects.create(
            metric_policy=Policy.METRIC_POLICY_CHOICES[0][0],
            name='policy0' + str(i),
            portal='{ "gt" : 80}',
            duration=timedelta(seconds=80),
            status=Policy.STATUS_CHOICES[0][0],
            level=Policy.LEVEL_CHOICES[1][0],
            nodes='all',
            creator='hpcadmin',
            wechat=True,
            sound=True,
        )
        Alarm(
            node='hostname0' + str(i),
            policy=p,
            status=s['status'],
            comment='alarm details',
        ).save()


@fixture
def operation_log():
    OperationLog.objects.create(
        module='module',
        operation='test',
        operator='operator'
    ).save()


@fixture
def bill_group():
    BillGroup().save()
