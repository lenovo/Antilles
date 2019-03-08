# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging
from abc import ABCMeta, abstractmethod

from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from six import add_metaclass

logger = logging.getLogger(__name__)


@add_metaclass(ABCMeta)
class DataTableView(APIView):
    columns_mapping = {}

    def get(self, request, *args, **kwargs):
        argss = json.loads(
            request.GET["args"]
        )

        argss = self.params(argss)

        query = self.get_query(request, *args, **kwargs)

        query = self.filters(query, argss.get('filters', None))  # filter

        query = self.global_search(query, argss)

        query = self.global_sort(query, argss)

        filtered_total = query.count()
        offset = argss['offset'] \
            if int(argss['offset']) < filtered_total else 0
        results = query[offset:offset + int(argss['length'])].all()
        offset = offset + len(results)

        return Response(
            {
                'offset': offset,
                'total': filtered_total,
                'data': [self.trans_result(result) for result in results],
            }
        )

    @abstractmethod
    def trans_result(self, result):
        pass

    @abstractmethod
    def get_query(self, request, *args, **kwargs):
        pass

    def global_search(self, query, argss):
        if 'search' not in argss:
            return query
        else:
            search = argss['search']
            props = search['props']
            keyword = search['keyword'].strip()

            q = Q()
            for field in props:
                prop = self.columns_mapping[field] \
                    if field in self.columns_mapping else field
                q |= Q(**{prop + '__icontains': keyword})

            return query.filter(q) if keyword != "" else query

    def global_sort_fields(self, argss):
        if 'sort' not in argss:
            return ['id']
        order = argss["sort"]
        if 'prop' not in order:
            return ['id']
        if order['prop'] in self.columns_mapping:
            prop = self.columns_mapping[order['prop']]
        else:
            prop = order['prop']
        return [
            ('' if order['order'] == 'ascending' else '-') +
            prop if argss['sort'] is not None else 'id'
        ]

    def global_sort(self, query, argss):
        return query.order_by(*self.global_sort_fields(argss))

    def filters(self, query, filters):
        if filters and len(filters) > 0:
            for field in filters:
                if field['prop'] in self.columns_mapping:
                    prop = self.columns_mapping[field['prop']]
                else:
                    prop = field['prop']
                query = query.filter(
                    **{
                        prop + '__{}'.format(
                            field['type']): field['values']
                    }
                )if len(field['values']) > 0 else query

        return query

    def params(self, args):
        return args


class ConfigView(APIView):
    def get(self, request):
        data = {
            'user': {
                'managed': settings.USE_LIBUSER
            },
            'hpc': {
                'enabled': 'antilles.hpc' in settings.INSTALLED_APPS
            },
            'scheduler': {
                'type': settings.SCHEDULER_SOFTWARE
            }
        }
        return Response(data)
