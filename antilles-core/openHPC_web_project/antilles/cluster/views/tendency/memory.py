# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.cluster.views.tendency.baseview import (
    GroupHeatBaseView, GroupTendencyBaseView, NodeHistoryBaseView,
)
from antilles.user.permissions import AsOperatorRole


class NodeHistoryMemoryView(NodeHistoryBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'node_mem_ratio'


class GroupTendencyMemoryView(GroupTendencyBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return 'nodegroup_mem_ratio'


class GroupHeatMemoryView(GroupHeatBaseView):
    permission_classes = (AsOperatorRole,)

    def get_db_table(self):
        return "node_mem_ratio"
