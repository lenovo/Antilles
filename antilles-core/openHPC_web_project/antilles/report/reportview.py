# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging
from collections import namedtuple
from datetime import datetime
from os import path

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, F, Sum
from django.utils.translation import trans_real, ugettext as _
from pytz import utc
from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.alarm.models import Alarm, Policy
from antilles.cluster.models import Node
from antilles.common.exceptions import InvalidParameterException
from antilles.common.helpers.filter_helper import (
    get_hostnames_from_filter, get_users_from_filter,
)
from antilles.common.utils import json_schema_validate
from antilles.optlog.models import OperationLog
from antilles.scheduler.models import Job
from antilles.user.models import BillGroup, User
from antilles.user.permissions import AsOperatorRole

from .etc import I18N
from .reportbase import GroupReportExporter, ReportExporter, TZinfoClass

logger = logging.getLogger(__name__)
context_tuple = namedtuple(
    "context", ['data', 'start_time', 'end_time', 'creator', 'create_time'])

g_TZinfo = TZinfoClass()


def _get_datetime(data):
    return datetime.fromtimestamp(int(data["start_time"]), tz=utc), \
           datetime.fromtimestamp(int(data["end_time"]), tz=utc)


def _get_timestamp(data):
    return int(data["start_time"]), int(data["end_time"])


def _get_create_info(data):
    return data["creator"], datetime.now(tz=utc)


def _get_head_title(target):
    return I18N[target]['title'], I18N[target]['head']


# filter ='job_user' or 'bill'
# if parmas job_user is empty ,this means is all users
def _get_params(data, filter=None):
    objectsdata = []
    if filter in data and isinstance(data[filter], list):
        objectsdata = data[filter]
        if objectsdata and filter == 'job_user':
            objectsdata = [user.username for user in User.objects.filter(
                username__in=objectsdata)]
            return objectsdata
        if objectsdata and filter == 'bill':
            objectsdata = [billgroup.name for billgroup in
                           BillGroup.objects.filter(name__in=objectsdata)]
            return objectsdata
        if not objectsdata and filter == 'job_user':
            objectsdata = [
                user.username for user in User.objects.all()]
        if not objectsdata and filter == 'bill':
            objectsdata = [billgroup[0] for billgroup in
                           BillGroup.objects.values_list('name')]
    return objectsdata


def _query_jobs_info(data):
    start_time, end_time = _get_timestamp(data)
    creator, create_time = _get_create_info(data)
    query = Job.objects.exclude(jobid="")
    users = data["job_user"] if "job_user" in data else []
    billgroups = data["bill"] if "bill" in data else []
    if users:
        query = query.filter(
            submiter__in=[user.strip() for user in users]
        )
    if billgroups:
        query = query.filter(
            billgroup__in=[bill.strip() for bill in billgroups]
        )
    query = query.filter(qtime__gte=start_time, qtime__lte=end_time)

    return query.all(), datetime.fromtimestamp(start_time,
                                               tz=utc), datetime.fromtimestamp(
        end_time, tz=utc), creator, create_time


def _query_jobs_details(data):
    job_columns = (
        "jobid", "jobname", "jobstatus", "queue", "qtime", "starttime",
        "endtime", "submiter", "cpuscount", "charge", "gpuscount", "gpucharge"
    )
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)

    tmp_values = objs.values_list(*job_columns)
    need_convert_idx = [
        job_columns.index("qtime"),
        job_columns.index("starttime"),
        job_columns.index("endtime")
    ]

    idx_jobstatus = job_columns.index("jobstatus")

    values = []
    for tmp_value in tmp_values:
        value = list(tmp_value)
        job_status = value[idx_jobstatus]
        need_exclude_idx = []
        if job_status.lower() == 'q':
            need_exclude_idx = [
                job_columns.index("starttime"),
                job_columns.index("endtime")
            ]
        elif job_status.lower() != 'c' and job_status.lower() != 'cancelled':
            need_exclude_idx = [job_columns.index("endtime")]

        for idx in need_convert_idx:
            if idx in need_exclude_idx:
                value[idx] = ""
                continue
            value[idx] = '{0:%Y-%m-%d %H:%M:%S}'.format(
                datetime.fromtimestamp(
                    value[idx], tz=g_TZinfo.get_FixedOffset)
            ) if (value[idx] and value[idx] != 0) else ""
        values.append(value)

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_jobs_statistics(data):
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)

    # one day is 86400 seconds, so calc the days by the method of timestamp
    # divided by 86400
    tmp_values = objs.annotate(
        date=(F("qtime") + g_TZinfo.get_seconds) / 86400 * 86400) \
        .values("date") \
        .annotate(jobcounts=Count("date"),
                  cpus=Sum("cpuscount"),
                  cpustime=Sum("charge"),
                  gpus=Sum("gpuscount"),
                  gpustime=Sum("gpucharge"))

    values = []
    for tmp_value in tmp_values:
        value = list(tmp_value.values())
        value[0] = '{0:%Y-%m-%d}'.format(
            datetime.fromtimestamp(tmp_value["date"],
                                   tz=g_TZinfo.get_FixedOffset))
        value[1] = tmp_value["jobcounts"]
        value[2] = tmp_value["cpus"]
        value[3] = tmp_value["cpustime"]
        value[4] = tmp_value["gpus"]
        value[5] = tmp_value["gpustime"]
        values.append(value)

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


'''
:parameter  list[OperationLog]
:return translate data: [(data)...]
'''


def _translate_operation_data(instances_list):
    return [(
        '{0:%Y-%m-%d %H:%M:%S}'.format(
            item.operate_time.astimezone(g_TZinfo.get_FixedOffset)
        ),
        _(item.module),
        item.operator,
        _(item.operation),
        ' '.join([
            item.operator,
            _(item.operation),
            _(item.module),
            _get_operationlog_target(item.target.all())
        ])
    ) for item in instances_list if len(instances_list)]


def _get_operationlog_target(target):
    return ','.join(
        [item_target.name for item_target in target if len(target)]
    )


def _query_operation_details(data):
    start_time, end_time = _get_datetime(data)
    creator, create_time = _get_create_info(data)
    objs = OperationLog.objects.filter(
        operate_time__gte=start_time,
        operate_time__lte=end_time
    )
    values = _translate_operation_data(objs)

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_alarm_info(data):
    alarm_level = {
        '0': None,
        '1': Policy.FATAL,
        '2': Policy.ERROR,
        '3': Policy.WARN,
        '4': Policy.INFO
    }

    start_time, end_time = _get_datetime(data)
    creator, create_time = _get_create_info(data)
    nodes = data["node"] if "node" in data else []
    level = data.get("event_level", "0")

    query = Alarm.objects.filter(
        create_time__gte=start_time,
        create_time__lte=end_time
    )
    if len(nodes) > 0:
        query = query.filter(node__in=[node.strip() for node in nodes])
    # 0: all; 1: fatal; 2:error; 3:warning; 4: info
    if level != "0":
        query = query.filter(policy__level=alarm_level[level])
    objs = query.all()

    return objs, start_time, end_time, creator, create_time


def _query_alarm_details(data):
    objs, start_time, end_time, creator, create_time = _query_alarm_info(data)

    alarm_columns = ("create_time", "policy__name", "node",
                     "policy__level", "status", "comment")

    # Make level to be consistent with UI
    level_map = {Policy.INFO: "Information",
                 Policy.WARN: "Warning",
                 Policy.ERROR: "Error",
                 Policy.FATAL: "Critical"}

    status_map = {Alarm.PRESENT: "Unconfirmed",
                  Alarm.CONFIRMED: "Confirmed",
                  Alarm.RESOLVED: "Fixed"}
    tmp_values = objs.values_list(*alarm_columns)

    values = []
    for tmp_value in tmp_values:
        value = list(tmp_value)
        value[0] = '{0:%Y-%m-%d %H:%M:%S}'.format(
            value[0].astimezone(g_TZinfo.get_FixedOffset)
        )
        if value[3] in level_map:
            value[3] = _(level_map[value[3]])
        else:
            value[3] = _(Policy.level_value(value[3]))

        if value[4] in status_map:
            value[4] = _(status_map[value[4]])
        else:
            value[4] = ""

        values.append(value)

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_alarm_statistics(data):
    data["node"], data["event_level"] = [], "0"
    objs, start_time, end_time, creator, create_time = _query_alarm_info(data)

    sql = {"hour": "date_trunc('hour', alarm_alarm.create_time)"}
    tmp_values = objs \
        .extra(select=sql) \
        .annotate(counts=Count("policy__level")) \
        .values("hour", "policy__level", "counts")

    datas = {}
    init_val = [0, 0, 0, 0, 0]
    level_idx = {logging.FATAL: 1,
                 logging.ERROR: 2,
                 logging.WARN: 3,
                 logging.INFO: 4}

    for tmp_val in tmp_values:
        tmp_val["hour"] = tmp_val["hour"].astimezone(g_TZinfo.get_FixedOffset)\
            .strftime("%Y-%m-%d")
        if tmp_val["hour"] not in datas:
            datas[tmp_val["hour"]] = [tmp_val["hour"]] + init_val

        datas[tmp_val["hour"]][
            level_idx[tmp_val["policy__level"]]] += tmp_val["counts"]
        # The last column is total alarm number
        datas[tmp_val["hour"]][-1] += tmp_val["counts"]

    values = datas.values()

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_user_details(data):
    job_columns = (
        "submiter", "jobid", "jobname",
        "jobstatus", "queue", "qtime", "starttime",
        "endtime", "submiter", "cpuscount", "charge", "gpuscount", "gpucharge"
    )
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)
    user_list = _get_params(data, filter='job_user')
    tmp_values = objs.values_list(*job_columns).order_by("qtime")
    need_convert_idx = [
        job_columns.index("qtime"),
        job_columns.index("starttime"),
        job_columns.index("endtime")
    ]

    idx_jobstatus = job_columns.index("jobstatus")

    values = []
    for user in user_list:
        group_data = []
        for tmp_value in tmp_values:
            if user == tmp_value[job_columns.index("submiter")]:
                value = list(tmp_value)
                job_status = value[idx_jobstatus]
                need_exclude_idx = []
                if job_status.lower() == 'q':
                    need_exclude_idx = [
                        job_columns.index("starttime"),
                        job_columns.index("endtime")
                    ]
                elif job_status.lower() != 'c' \
                        and job_status.lower() != 'cancelled':
                    need_exclude_idx = [job_columns.index("endtime")]

                for idx in need_convert_idx:
                    if idx in need_exclude_idx:
                        value[idx] = ""
                        continue
                    value[idx] = '{0:%Y-%m-%d %H:%M:%S}'.format(
                        datetime.fromtimestamp(
                            value[idx], tz=g_TZinfo.get_FixedOffset)
                    ) if (value[idx] and value[idx] != 0) else ""

                group_data.append(value[1:])
        values.append((user, group_data))

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator, create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_user_statistics(data):
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)

    tmp_values = objs \
        .annotate(date=F("qtime") / 86400 * 86400) \
        .values("submiter", "date", "submiter") \
        .annotate(jobcounts=Count("qtime"),
                  cpus=Sum("cpuscount"),
                  cpustime=Sum("charge"),
                  gpus=Sum("gpuscount"),
                  gpustime=Sum("gpucharge"))
    user_list = _get_params(data, filter='job_user')

    values = []
    for user in user_list:
        group_data = []
        for tmp_value in tmp_values:
            if user == tmp_value["submiter"]:
                value = list(tmp_value.values())
                value[0] = '{0:%Y-%m-%d}'.format(
                    datetime.fromtimestamp(
                        tmp_value["date"], tz=g_TZinfo.get_FixedOffset)
                )
                value[1] = tmp_value["submiter"]
                value[2] = tmp_value["jobcounts"]
                value[3] = tmp_value["cpus"]
                value[4] = tmp_value["cpustime"]
                value[5] = tmp_value["gpus"]
                value[6] = tmp_value["gpustime"]
                group_data.append(value)
        values.append((user, group_data))

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(
            g_TZinfo.get_FixedOffset), creator,
        create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_bill_details(data):
    job_columns = (
        "billgroup", "jobid", "jobname",
        "jobstatus", "queue", "qtime", "starttime",
        "endtime", "submiter", "cpuscount", "charge", "gpuscount", "gpucharge"
    )
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)
    bill_group_list = _get_params(data, filter='bill')

    tmp_values = objs.values_list(*job_columns).order_by("qtime")
    need_convert_idx = [
        job_columns.index("qtime"),
        job_columns.index("starttime"),
        job_columns.index("endtime")
    ]

    idx_jobstatus = job_columns.index("jobstatus")

    values = []
    for group_title in bill_group_list:
        group_data = []
        for tmp_value in tmp_values:
            if group_title == tmp_value[job_columns.index("billgroup")]:
                value = list(tmp_value)
                job_status = value[idx_jobstatus]
                need_exclude_idx = []
                if job_status.lower() == 'q':
                    need_exclude_idx = [
                        job_columns.index("starttime"),
                        job_columns.index("endtime")
                    ]
                elif job_status.lower() != 'c' \
                        and job_status.lower() != 'cancelled':
                    need_exclude_idx = [job_columns.index("endtime")]

                for idx in need_convert_idx:
                    if idx in need_exclude_idx:
                        value[idx] = ""
                        continue
                    value[idx] = '{0:%Y-%m-%d %H:%M:%S}'.format(
                        datetime.fromtimestamp(
                            value[idx], tz=g_TZinfo.get_FixedOffset)
                    ) if (value[idx] and value[idx] != 0) else ""
                group_data.append(value[1:])
        values.append((group_title, group_data))

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(
            g_TZinfo.get_FixedOffset), creator,
        create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def _query_bill_statistics(data):
    objs, start_time, end_time, creator, create_time = _query_jobs_info(data)

    tmp_values = objs \
        .annotate(date=F("qtime") / 86400 * 86400) \
        .values("billgroup", "date", "billgroup") \
        .annotate(jobcounts=Count("qtime"),
                  cpus=Sum("cpuscount"),
                  cpustime=Sum("charge"),
                  gpus=Sum("gpuscount"),
                  gpustime=Sum("gpucharge"))
    bill_group_list = _get_params(data, filter='bill')

    values = []
    for group_title in bill_group_list:
        group_data = []
        for tmp_value in tmp_values:
            if group_title == tmp_value["billgroup"]:
                value = list(tmp_value.values())
                value[0] = '{0:%Y-%m-%d}'.format(
                    datetime.fromtimestamp(
                        tmp_value["date"], tz=g_TZinfo.get_FixedOffset)
                )
                value[1] = tmp_value["billgroup"]
                value[2] = tmp_value["jobcounts"]
                value[3] = tmp_value["cpus"]
                value[4] = tmp_value["cpustime"]
                value[5] = tmp_value["gpus"]
                value[6] = tmp_value["gpustime"]
                group_data.append(value)
        values.append((group_title, group_data))

    return context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(
            g_TZinfo.get_FixedOffset), creator,
        create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()


def get_sql(hostname, table_name):
    if table_name == 'node_network':
        sql_in = "select %s from \"hour\".%s where host=\'%s\'" % (
            'value / 1048576', 'node_network_in', hostname)
        sql_out = "select %s from \"hour\".%s where host=\'%s\'" % (
            'value / 1048576', 'node_network_out', hostname)
        time_query = " and time > now() - 1h"
        sql = "%s %s;%s %s" % (sql_in, time_query, sql_out, time_query)
    else:
        sql = "select value from \"hour\".%s where host=\'%s\'" % (
            table_name,
            hostname
        )
        sql += " and time > now() - 1h"
    return sql


def handle_query_data(table_name, data):
    ret = []
    ret_in = []
    ret_out = []
    if table_name != 'node_network':
        for item in data:
            ret = item
            break
        return ret
    for item in data[0]:
        ret_in = item
        break

    for item in data[1]:
        ret_out = item
        break

    handle_key = ['value'][0]

    for index, itemd in enumerate(ret_in):
        try:
            value = "{0},{1}".format(
                round(itemd[handle_key], 2),
                round(ret_out[index][handle_key], 2)
            )
        except Exception:
            value = "0,0"
        ret.append({'time': itemd['time'], 'value': value})

    return ret


def get_sql_query_data(hostname, table_name):
    try:
        node = Node.objects.filter(hostname=hostname)
        if len(node) == 0:
            return [False, []]
        sql = get_sql(hostname, table_name)
        logger.info("sql: %s" % (sql,))
        data = cache.get(sql, epoch='s')
        data = handle_query_data(table_name, data)
        return [True, data]
    except Exception as e:
        logger.error(e.message)
        return [False, []]


def _query_node_running_info(request_data):
    result = []
    metrics = {
        'cpu': 'node_cpu',
        'mem': 'node_mem_ratio',
        'net': 'node_network'
    }
    if not request_data['node']:
        request_data['node'] = [node.hostname for node in Node.objects.all()]

    for node in request_data['node']:
        success, redis_data = get_sql_query_data(
            node, metrics[request_data['monitor_type']])
        if not success:
            continue
        if request_data['monitor_type'] == 'net':  # net
            data = [
                ('{0:%Y-%m-%d %H:%M:%S}'.format(
                    datetime.fromtimestamp(
                        int(val['time']), tz=g_TZinfo.get_FixedOffset
                    )
                ),
                 '{0}MB / {1}MB'.format(
                     int(float(val['value'].split(',')[0])),
                     int(float(val['value'].split(',')[1])))
                ) for val in redis_data
            ]
        else:  # cpu, mem
            data = [
                ('{0:%Y-%m-%d %H:%M:%S}'.format(
                    datetime.fromtimestamp(
                        int(val['time']), tz=g_TZinfo.get_FixedOffset
                    )
                ),
                 '{}%'.format((float(val['value'])))
                ) for val in redis_data
            ]

        result.append((node, data))
    return result


def _query_node_running_statistics(data):
    start_time, end_time = _get_datetime(data)
    creator, create_time = _get_create_info(data)
    try:
        values = _query_node_running_info(data)
    except Exception:
        raise
    context = context_tuple(
        values,
        start_time.astimezone(g_TZinfo.get_FixedOffset),
        end_time.astimezone(g_TZinfo.get_FixedOffset),
        creator,
        create_time.astimezone(g_TZinfo.get_FixedOffset)
    )._asdict()
    titles = I18N[data['target']][data['monitor_type']]
    context['headline'] = titles['head']
    context['title'] = titles['title']
    context['subtitle'] = titles['subtitle']
    return context


class ReportView(APIView):
    permission_classes = (AsOperatorRole,)

    config = {
        'alarm_details': (_query_alarm_details, ReportExporter),
        'alarm_statistics': (_query_alarm_statistics, ReportExporter),
        'jobs_details': (_query_jobs_details, ReportExporter),
        'jobs_statistics': (_query_jobs_statistics, ReportExporter),
        'operation_details': (_query_operation_details, ReportExporter),
        'user_details': (_query_user_details, GroupReportExporter),
        'user_statistics': (_query_user_statistics, GroupReportExporter),
        'bill_details': (_query_bill_details, GroupReportExporter),
        'bill_statistics': (_query_bill_statistics, GroupReportExporter),
        'node_running_statistics': (_query_node_running_statistics,
                                    GroupReportExporter),
    }

    @json_schema_validate({
        "type": "object",
        "properties": {
            "timezone_offset": {
                "type": "integer"
            },
            "language": {
                "type": "string"
            },
            "node": {
                # "type": "array",
                # "items": {
                #     "type": "string"
                # }
                "type": "object",
                "properties": {
                    "value_type": {"type": "string"},
                    "values": {"type": "array"}
                }
            },
            "monitor_type": {
                "type": "string",
                "minLength": 1,
            },
            "start_time": {
                "type": "integer",
                "minimum": 0,
            },
            "end_time": {
                "type": "integer",
                "minimum": 0,
            },
            "creator": {
                "type": "string",
                "minLength": 1,
            },
            "page_direction": {
                "type": "string",
                "enum": ["vertical", "landscape"]
            },
            "url": {
                "type": "string",
                "minLength": 1,
            },
            "bill": {
                "type": "array",
                "items": {
                    "type": "string"
                }
                # "type": "object",
                # "properties": {
                #     "value_type": {"type": "string"},
                #     "values": {"type": "array"}
                # }
            },
            "job_user": {
                # "type": "array",
                # "items": {
                #     "type": "string"
                # }
                "type": "object",
                "properties": {
                    "value_type": {"type": "string"},
                    "values": {"type": "array"}
                }
            },
        },
        "required": [
            "timezone_offset",
            "language",
            "start_time",
            "end_time",
            "creator",
            "page_direction"]
    })
    def post(self, request, filename):
        self.set_language(request)
        # set tzinfo
        get_tzinfo = int(request.data.get('timezone_offset', 0))
        g_TZinfo.set(minute=get_tzinfo)
        target, ext = path.splitext(filename)
        if target not in self.config or ext not in ['.html', '.pdf', '.xls']:
            raise InvalidParameterException

        action, exporter = self.config.get(target, (None, ReportExporter))
        request.data['target'] = target
        no_time_range = ['node_running_statistics']

        context = {
            'headline': I18N[target].get('head', None),
            'title': I18N[target].get('title', None),
            'subtitle': "",
            'doctype': ext[1:],
            'template': path.join('report', target + '.html'),
            'page_direction': request.data['page_direction'],
            'fixed_offset': g_TZinfo.get_FixedOffset,
            'time_range_flag': target in no_time_range
        }
        # Handle 'job_user' and 'node' parameters to \
        # compatible with the following code
        if "job_user" in request.data:
            request.data["job_user"] = \
                get_users_from_filter(request.data["job_user"])
        if "node" in request.data:
            request.data["node"] = \
                get_hostnames_from_filter(request.data["node"])
        try:
            context.update(action(request.data))
        except Exception:
            logger.exception(
                "Generate {0} {1} report failed".format(target, ext))
            raise
        result = exporter(**context).report_export()

        return Response({'data': result})

    def set_language(self, request):
        set_language = request.data.get('language', False)
        back_language = dict(settings.LANGUAGES)
        if set_language in back_language:
            language = set_language
        else:
            language = settings.LANGUAGE_CODE
        trans_real.activate(language)


class JobReportPreview(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request, category):
        format_data = {"total": 0, "data": []}
        category_mapping = {'user': 'user', 'job': 'job',
                            'bill_group': 'bill_group'}
        start_time = int(request.GET["start_time"])
        end_time = int(request.GET["end_time"])
        filters = json.loads(request.GET["filters"])
        get_tzinfo = int(request.GET['timezone_offset'])
        g_TZinfo.set(minute=get_tzinfo)
        if category not in category_mapping:
            return format_data
        category = category_mapping[category]
        query = Job.objects.exclude(jobid="")
        if category == 'bill_group':
            filters = filters if filters else \
                [billgroup[0] for billgroup in
                 BillGroup.objects.values_list('name')]
            query = query.filter(
                billgroup__in=[bill.strip() for bill in filters]
            )
        else:
            filters = get_users_from_filter(filters)
            if filters:
                query = query.filter(
                    submiter__in=[user.strip() for user in filters]
                )
        query = query.filter(qtime__gte=start_time, qtime__lte=end_time)
        tmp_values = query.annotate(
            date=(F("qtime") - get_tzinfo * 60) / 86400 * 86400) \
            .values("submiter", "date", "billgroup") \
            .annotate(jobcounts=Count("date"),
                      cpus=Sum("cpuscount"),
                      cpustime=Sum("charge"),
                      gpus=Sum("gpuscount"),
                      gpustime=Sum("gpucharge"))

        format_data['data'] = []
        for tmp_value in tmp_values:
            values = {}
            if category is not 'job':
                values['name'] = tmp_value["submiter"] \
                    if category == 'user' else tmp_value["billgroup"]
            values['start_time'] = '{0:%Y-%m-%d}'.format(
                datetime.fromtimestamp(tmp_value["date"],
                                       tz=g_TZinfo.get_FixedOffset))
            values['job_count'] = tmp_value["jobcounts"]
            values['cpu_count'] = tmp_value["cpus"]
            values['cpu_runtime'] = tmp_value["cpustime"]
            values['gpu_count'] = tmp_value["gpus"]
            values['gpu_runtime'] = tmp_value["gpustime"]
            format_data['data'].append(values)

        format_data['total'] = len(tmp_values)
        return Response(format_data)


class AlarmReportPreview(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request):
        format_data = {"total": 0, "data": []}
        start_time = int(request.GET["start_time"])
        end_time = int(request.GET["end_time"])
        get_tzinfo = int(request.GET['timezone_offset'])
        g_TZinfo.set(minute=get_tzinfo)

        data = {'start_time': start_time, 'end_time': end_time, 'creator': ''}
        datas = _query_alarm_statistics(data)

        format_data['data'] = []
        for data in datas['data']:
            val = {}
            val["alarm_time"] = data[0]
            val['critical'] = data[1]
            val['error'] = data[2]
            val['warning'] = data[3]
            val['info'] = data[4]
            val['num_total'] = data[-1]
            format_data['data'].append(val)
            format_data['total'] += val['num_total']

        return Response(format_data)


class OperationReportPreview(APIView):
    permission_classes = (AsOperatorRole,)

    def trans_result(self, category, val):
        if category == 'network':
            _in = float(val.split(' / ')[0].split('MB')[0])
            _out = float(val.split(' / ')[1].split('MB')[0])
            val = _in + _out
        else:
            val = val.split('%')[0]
        return str(val)

    def get(self, request, category):
        format_data = {"total": 0, "data": []}
        # filters = json.loads(request.GET["filters"])
        node_filter = json.loads(request.GET["filters"])
        filters = get_hostnames_from_filter(node_filter)
        get_tzinfo = int(request.GET['timezone_offset'])
        g_TZinfo.set(minute=get_tzinfo)

        metrics = {
            'cpu': 'cpu',
            'memory': 'mem',
            'network': 'net'
        }

        monitor_type = metrics[category]
        data = {'start_time': 0, 'end_time': 0, 'creator': '',
                'node': filters, 'monitor_type': monitor_type,
                'target': 'node_running_statistics'}
        datas = _query_node_running_statistics(data)

        format_data['data'] = []
        for data in datas['data']:
            values = {"history": [], "hostname": data[0], "type": category}
            for val in data[1]:
                tmp = {"time": val[0], "usage": self.trans_result(
                    category, val[1])}
                values["history"].append(tmp)
            format_data['data'].append(values)

        format_data['total'] = len(datas['data'])
        return Response(format_data)
