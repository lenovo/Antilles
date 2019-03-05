# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime
from rest_framework.response import Response

from antilles.common.exceptions import InvalidParameterException
from antilles.common.helpers.filter_helper import get_users_from_filter
from antilles.common.views import DataTableView
from antilles.optlog.models import LogDetail, OperationLog

logger = logging.getLogger(__name__)


class OpLogView(DataTableView):
    columns_mapping = {
        'id': 'id',
        'operator': 'operator',
        'module': 'module',
        'operation': 'operation',
        'operate_time': 'operate_time',
        'target': 'target'
    }

    def trans_result(self, result):
        return {
            'id': result.id,
            'operator': result.operator,
            'module': result.module,
            'operation': result.operation,
            'operate_time': localtime(result.operate_time),
            'target': LogDetail.objects.filter(optlog=result.id).values(
                'object_id', 'name')
        }

    def get_query(self, request, *args, **kwargs):
        return OperationLog.objects

    def filters(self, query, filters):
        for field in filters:
            values = []
            if field['prop'] == 'operate_time':
                for times in field['values']:
                    values.append(parse_datetime(times))
                field['values'] = values
            # Handler 'operator' filter to compatible with following code
            if field['prop'] == 'operator':
                field['values'] = get_users_from_filter(field)
                field['value_type'] = 'username'
        return super(OpLogView, self).filters(query, filters)


class LatestOpLogView(OpLogView):

    def get(self, request, *args, **kwargs):
        queryparams = request.GET.get("counts")

        if queryparams is None:
            raise InvalidParameterException

        counts = int(queryparams)

        query = self.get_query(request, *args, **kwargs)

        query = self.global_sort(query, None)

        q_cnts = query.count()

        length = counts if q_cnts >= counts else q_cnts

        results = query[0:length].all()

        return Response(
            {
                'data': [self.trans_result(result) for result in results],
            }
        )

    def global_sort_fields(self, argss):
        return ['-operate_time']
