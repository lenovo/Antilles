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


class NodeHistoryLoadView(NodeHistoryBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'node_load'


class GroupTendencyLoadView(GroupTendencyBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'nodegroup_load'


class GroupHeatLoadView(GroupHeatBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return "node_load"
