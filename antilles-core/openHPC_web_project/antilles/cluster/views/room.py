# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.cluster.models import Node, Room
from antilles.user.permissions import AsOperatorRole


class RoomView(APIView):
    permission_classes = (AsOperatorRole,)

    def get(self, request):
        return Response({
            'rooms': [
                self.get_statics(room)
                for room in Room.objects.iterator()
            ]
        })

    def get_statics(self, room):
        node_num = Node.objects.filter(
            rack__row__room=room
        ).count()
        return {
            'id': room.id,
            'name': room.name,
            'location': room.location,
            'node_num': node_num
        }
