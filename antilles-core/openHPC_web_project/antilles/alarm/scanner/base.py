# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging

from antilles.common.helpers.filter_helper import (
    get_hostnames_from_filter, parse_nodes_filter_from_db,
)

logger = logging.getLogger(__name__)


class Base(object):
    def __init__(self, policy):
        self._policy = policy
        self._duration = int(self._policy.duration.total_seconds())
        self._aggregate, self._val = self._parse_portal()

    @property
    def _nodes(self):
        # if "all" != self._policy.nodes.lower():
        #     return self._policy.nodes.split(";")
        # else:
        #     return []
        node_filter = parse_nodes_filter_from_db(self._policy.nodes)
        return get_hostnames_from_filter(node_filter)

    def _parse_portal(self):
        rep = ""
        val = 0.0
        method = ""
        try:
            portal = json.loads(str(self._policy.portal))
            if portal and (portal.keys()[0]).startswith('$'):
                rep, val = portal.items()[0]
            if rep == "$lt" or rep == "$lte":
                method = "max"
            elif rep == "$gt" or rep == "$gte":
                method = "min"
        except Exception:
            logger.exception("Portal {0} in policy {1} is unvalid."
                             .format(self._policy.portal,
                                     self._policy.metric_policy))
        return method, val
