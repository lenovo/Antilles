# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from abc import ABCMeta, abstractmethod

from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from six import add_metaclass

from antilles.cluster.models import Node, NodeGroup

CATEGORY_MAPPING = {
    'hour': '1h',
    'day': '1d',
    'week': '1w',
    'month': '31d'
}

logger = logging.getLogger(__name__)


@add_metaclass(ABCMeta)
class NodeHistoryBaseView(APIView):

    TENDENCY_INTERVAL_TIME = {
        'hour': '30s',
        'day': '12m',
        'week': '1h24m',
        'month': '6h12m'
    }

    def get(self, request, pk, category):
        hostname = Node.objects.get(id=pk).hostname
        sql_history = self.get_history_sql(request, category, hostname)
        logger.info("sql: %s" % (sql_history,))
        history = cache.get(sql_history, epoch='s')
        history = self.handle_query_data(history)
        sql_current = self.get_current_sql(category, hostname)
        logger.info("sql: %s" % (sql_current,))
        current = self.get_current_data(sql_current)
        return self.return_success(history, current)

    @abstractmethod
    def get_db_table(self):
        pass

    @property
    def get_scale_data(self):
        ''' sql: select [sql value] **
            handle_key: handle_query_data use handle_key'''
        return {'sql': 'last(value) as value', 'handle_key': ['value']}

    def get_history_sql(self, request, *args, **kwargs):
        category = args[0]
        hostname = args[1]
        sql = "select {field_sql} from \"{categ}\".{table} where \
         host=\'{host}\'".format(
                field_sql=self.get_scale_data['sql'],
                categ=category,
                table=self.get_db_table(),
                host=hostname)
        sql += " and time > now() - %s" % (CATEGORY_MAPPING[category],)
        sql += " group by time(%s)" % (self.TENDENCY_INTERVAL_TIME[category],)
        return sql

    def get_current_sql(self, category, hostname):
        sql = "select last(value) from \"{categ}\".{table} where " \
              "host=\'{host}\'".format(categ=category,
                                       table=self.get_db_table(),
                                       host=hostname
                                       )
        return sql

    def get_current_data(self, sql):
        ret = cache.get(sql)
        current = 0
        for p in ret.get_points():
            current = p.get('last', 0)
        return current

    def handle_query_data(self, data):
        ret = []
        for item in data:
            ret = item
            break
        return ret

    def return_success(self, history, current):
        return_data = {"history": history if history else [],
                       'current': current}
        return Response(return_data, status=HTTP_200_OK)


@add_metaclass(ABCMeta)
class GroupTendencyBaseView(APIView):

    TENDENCY_INTERVAL_TIME = {
        'hour': '30s',
        'day': '12m',
        'week': '1h24m',
        'month': '6h12m'
    }

    def get(self, request, pk, category, format=None):
        groupobject = NodeGroup.objects.get(id=pk)
        groupname = groupobject.name
        sql_history = self.get_history_sql(request, category, groupname)
        logger.info("sql: %s", sql_history)
        history = cache.get(sql_history, epoch='s')
        history = self.handle_query_data(history)
        sql_current = self.get_current_sql(category, groupname)
        logger.info("sql: %s", sql_current)
        current = self.get_current_data(sql_current)
        return self.return_success(history, current)

    @abstractmethod
    def get_db_table(self):
        pass

    @property
    def get_scale_data(self):
        ''' sql: select [sql value] **
            handle_key: handle_query_data use handle_key'''
        return {'sql': 'last(value) as value', 'handle_key': ['value']}

    def get_history_sql(self, request, *args, **kwargs):
        category = args[0]
        groupname = args[1]
        sql = "select {field_sql} from \"{categ}\".{table} \
        where \"host\"=\'{host}\'".format(
            field_sql=self.get_scale_data['sql'],
            categ=category,
            table=self.get_db_table(),
            host=groupname)

        sql += " and time > now() - %s" % (CATEGORY_MAPPING[category],)
        sql += " group by time(%s)" % (self.TENDENCY_INTERVAL_TIME[category],)
        return sql

    def get_current_sql(self, category, groupname):
        sql = "select last(value) from \"{categ}\".{table} where " \
              "host=\'{host}\'".format(categ=category,
                                       table=self.get_db_table(),
                                       host=groupname
                                       )
        return sql

    def get_current_data(self, sql):
        ret = cache.get(sql)
        current = 0
        for p in ret.get_points():
            current = p.get('last', 0)
        return current

    def handle_query_data(self, data, *args, **kwargs):
        ret = []
        for item in data:
            ret = item
            break
        return ret

    def return_success(self, history, current):
        return_data = {"history": history if history else [],
                       # last value may be None
                       'current': current,
                       "total": 0}
        return Response(return_data, status=HTTP_200_OK)


@add_metaclass(ABCMeta)
class GroupHeatBaseView(APIView):

    LAST_VALUE_PERIOD = '30s'

    def get(self, request, pk):
        groupobject = NodeGroup.objects.get(id=int(pk))
        nodesdata = list(groupobject.nodes.values("id", "hostname"))
        for item in nodesdata:
            sql = self.get_sql(item['hostname'])
            logger.info("sql:%s" % sql)
            data = cache.get(sql)
            data = self.handle_query_data(data)
            item.update(data)
        return self.return_success(nodesdata)

    @abstractmethod
    def get_db_table(self):
        pass

    @property
    def get_scale_data(self):
        ''' sql: select [sql value] **
            handle_key: handle_query_data use handle_key'''
        return {'sql': 'LAST(value)', 'handle_key': ['last']}

    def get_sql(self, hostname):
        table = self.get_db_table()
        last_period = self.LAST_VALUE_PERIOD

        sql = "select {field_sql} from hour.{table} where  host=\'{host}\'\
         and  time > now() - {period}".format(
            field_sql=self.get_scale_data['sql'],
            table=table,
            host=hostname,
            period=last_period)
        return sql

    def handle_query_data(self, data):
        try:
            handle_key = self.get_scale_data['handle_key'][0]
            for item in data:
                return {'value': item[0][handle_key]}
            else:
                return {'value': None}
        except Exception:
            return {'value': None}

    def return_success(self, data, *args, **kwargs):
        return Response({"heat": data}, status=HTTP_200_OK)
