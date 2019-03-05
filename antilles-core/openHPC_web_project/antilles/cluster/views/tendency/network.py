# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.core.cache import cache

from antilles.cluster.views.tendency.baseview import (
    CATEGORY_MAPPING, GroupHeatBaseView, GroupTendencyBaseView,
    NodeHistoryBaseView,
)
from antilles.user.permissions import AsOperatorRole


class NodeHistoryNetworkView(NodeHistoryBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'node_network'

    @property
    def get_scale_data(self):
        return {'sql': 'last(value)/1048576 as value', 'handle_key': ['value']}

    def get_history_sql(self, request, *args, **kwargs):
        category = args[0]
        hostname = args[1]
        db_in = "%s_in" % self.get_db_table()
        db_out = "%s_out" % self.get_db_table()
        sql_in = "select {field_sql} from \"{categ}\".{table} where \
         host=\'{host}\'".format(
            field_sql=self.get_scale_data['sql'],
            categ=category,
            table=db_in,
            host=hostname
        )
        sql_out = "select {field_sql} from \"{category}\".{table} where \
         host=\'{host}\'".format(
                field_sql=self.get_scale_data['sql'],
                category=category,
                table=db_out,
                host=hostname
            )
        time_query = " and time > now() - %s" % (CATEGORY_MAPPING[category],)
        time_query += " group by time(%s)" % (
            self.TENDENCY_INTERVAL_TIME[category],)
        sql = "%s %s;%s %s" % (sql_in, time_query, sql_out, time_query)
        return sql

    def get_current_sql(self, category, hostname):
        db_in = "%s_in" % self.get_db_table()
        db_out = "%s_out" % self.get_db_table()

        sql_in = "select last(value)/1048576 from \"{categ}\".{table} where " \
                 "host=\'{host}\'".format(categ=category,
                                          table=db_in,
                                          host=hostname
                                          )

        sql_out = "select last(value)/1048576 from \"{categ}\".{table} where " \
                  "host=\'{host}\'".format(categ=category,
                                           table=db_out,
                                           host=hostname
                                           )
        return sql_in + ';' + sql_out

    def get_current_data(self, sql):
        ret = cache.get(sql)
        current = [str(p.get('last', '0')) for a in ret for p in a.get_points()]
        return ','.join(current)

    def handle_query_data(self, data):
        ret = []
        ret_in = []
        for item in data[0]:
            ret_in = item
            break

        for item in data[1]:
            ret_out = item
            break

        handle_key = self.get_scale_data['handle_key'][0]

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


class GroupTendencyNetworkView(GroupTendencyBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'nodegroup_network'

    @property
    def get_scale_data(self):
        return {'sql': 'last(value)/1048576 as value', 'handle_key': ['value']}

    def get_history_sql(self, request, *args, **kwargs):
        category = args[0]
        groupname = args[1]
        db_in = "%s_in" % self.get_db_table()
        db_out = "%s_out" % self.get_db_table()
        sql_in = "select {field_sql} from \"{categ}\".{table} where \
        host=\'{host}\'".format(
                field_sql=self.get_scale_data['sql'],
                categ=category,
                table=db_in,
                host=groupname
            )
        sql_out = "select {field_sql} from \"{categ}\".{table} where \
        host=\'{host}\'".format(
                field_sql=self.get_scale_data['sql'],
                categ=category,
                table=db_out,
                host=groupname
            )

        time_query = " and time > now() - %s" % (CATEGORY_MAPPING[category],)
        time_query += " group by time(%s)" % (
            self.TENDENCY_INTERVAL_TIME[category],)
        sql = "%s %s;%s %s" % (sql_in, time_query, sql_out, time_query)
        return sql

    def get_current_sql(self, category, groupname):
        db_in = "%s_in" % self.get_db_table()
        db_out = "%s_out" % self.get_db_table()

        sql_in = "select last(value) from \"{categ}\".{table} where " \
                 "host=\'{host}\'".format(categ=category,
                                          table=db_in,
                                          host=groupname
                                          )

        sql_out = "select last(value) from \"{categ}\".{table} where " \
                  "host=\'{host}\'".format(categ=category,
                                           table=db_out,
                                           host=groupname
                                           )
        return sql_in + ';' + sql_out

    def get_current_data(self, sql):
        ret = cache.get(sql)
        current = [str(p.get('last', '0')) for a in ret for p in a.get_points()]
        return ','.join(current)

    def handle_query_data(self, data):
        ret = []
        ret_in = []
        ret_out = []
        for item in data[0]:
            ret_in = item
            break

        for item in data[1]:
            ret_out = item
            break

        handle_key = self.get_scale_data['handle_key'][0]

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


class GroupHeatNetworkView(GroupHeatBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'node_network'

    @property
    def get_scale_data(self):
        return {'sql': 'last(value)/1048576', 'handle_key': ['last']}

    def get_sql(self, hostname):
        db_in = "%s_in" % self.get_db_table()
        db_out = "%s_out" % self.get_db_table()
        sql_in = "select {field_sql} from hour.{table} where \
         host=\'{host}\' and  time > now() - {period}".format(
            field_sql=self.get_scale_data['sql'],
            table=db_in,
            host=hostname,
            period=self.LAST_VALUE_PERIOD
        )
        sql_out = "select {field_sql} from hour.{table} where \
         host=\'{host}\' and  time > now() - {period}".format(
            field_sql=self.get_scale_data['sql'],
            table=db_out,
            host=hostname,
            period=self.LAST_VALUE_PERIOD
        )
        sql = "%s;%s" % (sql_in, sql_out)
        return sql

    def handle_query_data(self, data):
        handle_key = self.get_scale_data['handle_key'][0]
        ret_in = []
        for item in data[0]:
            ret_in = item
            break

        for item in data[1]:
            ret_out = item
            break
        try:
            value = "{0},{1}".format(
                round(ret_in[0][handle_key], 2),
                round(ret_out[0][handle_key], 2)
            )
        except Exception:
            value = "0,0"

        return {'value': value}


class GroupTendencyJob(GroupTendencyBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'nodegroup_job'


class GroupHeatJob(GroupHeatBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'node_job'
