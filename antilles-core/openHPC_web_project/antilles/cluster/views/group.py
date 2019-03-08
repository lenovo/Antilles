# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.cluster.models import NodeGroup
from antilles.user.permissions import AsOperatorRole

logger = logging.getLogger(__name__)


class NodeGroupView(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request):
        return Response({
            'groups': [
                {
                    'groupname': grp.name,
                    'id': grp.id
                }
                for grp in NodeGroup.objects.iterator()
            ]
        })
