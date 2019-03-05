# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from antilles.cluster.models import Node, NodeGroup
from antilles.cluster.views.tendency.baseview import CATEGORY_MAPPING
from antilles.user.permissions import AsOperatorRole

logger = logging.getLogger(__name__)


LAST_VALUE_PERIOD = '30s'


class NodeHistoryGpuView(APIView):
    permission_classes = (AsOperatorRole,)

    TENDENCY_INTERVAL_TIME = {
        'hour': '30s',
        'day': '12m',
        'week': '1h24m',
        'month': '6h12m'
    }

    def get(self, request, pk, index, time_unit, category, format=None):
        hostname = Node.objects.get(id=pk).hostname
        sql = self.get_sql(request, hostname, index, time_unit, category)
        logger.info("gpu history sql: %s" % sql)
        data = cache.get(sql, epoch='s')
        data = self.handle_query_data(data)
        return self.return_success(data)

    def get_sql(self, request, hostname, index, time_unit, category):
        table_mapping = {
            "util": "node_gpu_util",
            "memory": "node_gpu_mem_pct",
            "temperature": "node_gpu_temp"
        }
        db_table = table_mapping[category]
        sql = "select last(value) as value from \"{categ}\".{table} \
        where host=\'{host}\' and index=\'{index}\'".format(
            categ=time_unit,
            table=db_table,
            host=hostname,
            index=index)
        time_query = " and time > now() - %s" % (
            CATEGORY_MAPPING[time_unit],)
        time_query += " group by time(%s)" % (
            self.TENDENCY_INTERVAL_TIME[time_unit],)
        return sql + time_query

    def handle_query_data(self, data):
        ret = []
        for item in data:
            ret = item
            break
        return ret

    def return_success(self, data, *args, **kwargs):
        return_data = {"msg": "",
                       "history": data if data else [],
                       # last value may be None
                       'current': data[-2]['value'] if len(data) >= 2 else None}
        return Response(return_data, status=HTTP_200_OK)


class GroupHeatGpuView(APIView):
    permission_classes = (AsOperatorRole,)

    def trans_result(self, result, category, used_table):
        used, value = self.get_sql_query_data(
            category, result.hostname, used_table)
        return {
            'id': result.id,
            'hostname': result.hostname,
            'value': value,
            'used': used,
        }

    def get_sql_query_data(self, table_name, hostname, used_table):
        query_sql = "select index,last(value) from hour.{table_name} \
        where host='{hostname}' and time > now() - {period} \
        group by index;".format(
            table_name=table_name,
            hostname=hostname,
            period=LAST_VALUE_PERIOD)
        used_sql = "select index,last(value) from hour.{table_name} \
        where host='{hostname}' and time > now() - {period} \
        group by index;".format(
            table_name=used_table,
            hostname=hostname,
            period=LAST_VALUE_PERIOD)
        sql = query_sql + used_sql
        used = []
        value = []
        logger.info("gpu heat sql: %s" % sql)
        data = cache.get(sql, epoch='s')
        value_data = []
        used_data = []
        try:
            for item in data[0]:
                value_data.append(item[0])

            for item in data[1]:
                used_data.append(item[0])

            for index, ivalue in enumerate(value_data):
                if used_data[index]['index'] == ivalue['index']:
                    use_flag = 1 if used_data[index]['last'] > 0 else 0
                    used.append(use_flag)
                    value.append(ivalue['last'])
        except Exception as e:
            logger.error(e.message)

        return used, value

    def get_all_gpu_nodes_list(self, table):
        sql = "select host,last(value) from {table} \
        where time > now() - {period} group by host".format(
            table=table,
            period=LAST_VALUE_PERIOD
        )
        data = cache.get(sql)
        return [item[1]["host"] for item in data.keys()]

    def get(self, request, pk, category, format=None):
        format_data = {"currentPage": 0, "offset": 0, "total": 0, "nodes": []}
        currentPage = int(request.GET["currentPage"])
        offset = int(request.GET["offset"])
        category_mapping = {
            'memory': 'node_gpu_mem_pct',
            'util': 'node_gpu_util',
            'temperature': 'node_gpu_temp'
        }

        used_table = 'node_gpu_process'

        try:
            nodegroup = NodeGroup.objects.filter(id=int(pk))
            gpunodes_list = self.get_all_gpu_nodes_list(used_table)
            nodes = nodegroup[0].nodes.filter(
                hostname__in=gpunodes_list).order_by("id")
            ncnts = nodes.count()
            if not ncnts:
                format_data["offset"] = offset
                format_data["currentPage"] = currentPage
                return Response(format_data, status=HTTP_200_OK)
        except Exception as e:
            logger.error(e.message)
            return Response(format_data, status=HTTP_200_OK)
        if category in category_mapping:
            category = category_mapping[category]
            format_data["total"] = ncnts
            page_up_sum = offset * (currentPage - 1)
            start_idx = 0 if page_up_sum > ncnts else page_up_sum
            results = nodes[start_idx:start_idx + offset]
            format_data["offset"] = offset
            format_data["currentPage"] = currentPage
            format_data["nodes"] = [] if not nodes else \
                [self.trans_result(result, category, used_table)
                 for result in results]

        return Response(format_data, status=HTTP_200_OK)
