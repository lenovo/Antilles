# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from inspect import getcallargs

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from six import raise_from

from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog

from ..models import BillGroup, Deposit, User
from ..permissions import AsAdminRole, AsOperatorRole
from .exceptions import (
    BillroupAlreadyExistsException, RemoveBillgroupHasMemberException,
)

logger = logging.getLogger(__name__)


class BillGroupListView(APIView):
    permission_classes = (AsAdminRole, )

    @AsOperatorRole
    def get(self, request):
        billgroups = BillGroup.objects.iterator()
        return Response([b.as_dict() for b in billgroups])

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 1
            },
            'charge_rate': {
                'type': 'number',
                'minimum': 0
            },
            'balance': {
                'type': 'number',
                'minimum': 0
            },
            'description': {
                'type': 'string',
            }
        },
        'required': [
            'name',
            'charge_rate',
            'balance'
        ]
    })
    def post(self, request):
        valid_param = getcallargs(BillGroup.objects.create, **request.data)
        logger.info(valid_param)
        try:
            billgroup = BillGroup.objects.create(**request.data)
            EventLog.opt_create(
                request.user.username, EventLog.billgroup, EventLog.create,
                [(billgroup.id, billgroup.name)]
            )
        except IntegrityError as e:
            raise_from(
                BillroupAlreadyExistsException, e
            )
        return Response(billgroup.as_dict())


class BillGroupDetailView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request, pk):
        return Response(BillGroup.objects.get(id=pk).as_dict())

    def delete(self, request, pk):
        obj = BillGroup.objects.get(id=pk)

        try:
            data = obj.as_dict()
            obj.delete()
        except ProtectedError as e:
            raise_from(
                RemoveBillgroupHasMemberException, e
            )
        EventLog.opt_create(
            request.user.username, EventLog.billgroup, EventLog.delete,
            [(data['id'], data['name'])]
        )
        return Response(data)

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            },
            'charge_rate': {
                'type': 'number',
                'minimum': 0
            },
            'description': {
                'type': 'string'
            }
        },
        'required': [
            'name',
            'charge_rate'
        ]
    })
    def patch(self, request, pk):
        try:
            BillGroup.objects.filter(id=pk).update(
                **request.data
            )
        except IntegrityError as e:
            raise_from(
                BillroupAlreadyExistsException, e
            )
        EventLog.opt_create(
            request.user.username, EventLog.billgroup, EventLog.update,
            [(pk, request.data['name'])]
        )
        return Response(BillGroup.objects.get(id=pk).as_dict())


class DepositListView(APIView):
    permission_classes = (AsAdminRole, )

    def get(self, request):
        return Response([d.as_dict() for d in Deposit.objects.iterator()])

    @json_schema_validate({
        'type': 'object',
        'properties': {
            'user': {
                'type': 'string'
            },
            'bill_group': {
                'type': 'integer',
                'minimum': 0
            },
            'credits': {
                'type': 'number',
            }
        },
        'required': [
            'user',
            'bill_group',
            'credits'
        ]
    })
    def post(self, request):
        user = User.objects.get(username=request.data['user'])
        input_bill_group = request.data['bill_group']
        bill_group = BillGroup.objects.get(id=input_bill_group)
        deposit = Deposit.objects.create(
            user=user,
            bill_group=bill_group,
            credits=float(
                request.data['credits']
            ),
            apply_time=timezone.now(),
            approved_time=timezone.now()
        )
        bill_group.balance += deposit.credits
        bill_group.balance = round(bill_group.balance, 2)
        bill_group.save()

        EventLog.opt_create(
            self.request.user.username,
            EventLog.deposit,
            DespositEventLog.action(deposit.credits),
            EventLog.make_list(
                deposit.id,
                '{0} {1:0.2f}'.format(bill_group.name, abs(deposit.credits))
            )
        )
        return Response(deposit.as_dict())


class DepositDetailView(APIView):
    permission_classes = (AsAdminRole,)

    def get(self, request, pk):
        return Response(Deposit.objects.get(id=pk).as_dict())

    def delete(self, request, pk):
        Deposit.objects.get(id=pk).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class DespositEventLog(EventLog):
    @classmethod
    def action(cls, value):
        return cls.recharge if (float(value) >= 0) else cls.chargeback
