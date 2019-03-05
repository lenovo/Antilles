# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.cluster.views.tendency.baseview import (
    GroupHeatBaseView, GroupTendencyBaseView, NodeHistoryBaseView,
)
from antilles.user.permissions import AsOperatorRole


class NodeHistoryTemperatureView(NodeHistoryBaseView):
    permission_classes = (AsOperatorRole,)

    TENDENCY_INTERVAL_TIME = {
        'hour': '60s',
        'day': '12m',
        'week': '1h24m',
        'month': '6h12m'
    }

    LAST_VALUE_PERIOD = '300s'

    def get_db_table(self):
        return 'node_temp'


class GroupTendencyTemperatureView(GroupTendencyBaseView):
    permission_classes = (AsOperatorRole,)

    TENDENCY_INTERVAL_TIME = {
        'hour': '60s',
        'day': '12m',
        'week': '1h24m',
        'month': '6h12m'
    }

    LAST_VALUE_PERIOD = '300s'

    def get_db_table(self):
        return 'nodegroup_temp'


class GroupHeatTemperatureView(GroupHeatBaseView):
    permission_classes = (AsOperatorRole,)

    LAST_VALUE_PERIOD = '300s'

    def get_db_table(self):
        return "node_temp"
