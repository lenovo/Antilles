# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

ROLE_ADMIN = 300
ROLE_OPERATOR = 200
ROLE_USER = 100

USER_ROLES = [
    (ROLE_ADMIN, 'admin'),
    (ROLE_OPERATOR, 'operator'),
    (ROLE_USER, 'user'),
]


class BaseRole(permissions.BasePermission):

    def __new__(cls, func=None):
        """
        Overwrite __new__ for use premission class as decorator

        example:
        >>> class TestView(APIView):
        ...     # if use class as decorator, __new__ get a argument func
        ...     @AsUserRole
        ...     def get(self, request):
        ...         pass

        premission defined by decorator will **overwrite** class premission
        """
        if func:        # use as decorator
            func.permission_class = cls
            return func
        else:
            return permissions.BasePermission.__new__(cls)

    def floor(self):
        pass

    def has_permission(self, request, view):
        if not request.user:
            return False

        if isinstance(request.user, AnonymousUser):
            return False

        # if defined method permission
        method = getattr(view, request.method.lower())
        method_permission = getattr(method, 'permission_class', None)
        if method_permission:
            return request.user.role >= method_permission.floor

        return request.user.role >= self.floor


class AsUserRole(BaseRole):
    floor = ROLE_USER


class AsOperatorRole(BaseRole):
    floor = ROLE_OPERATOR


class AsAdminRole(BaseRole):
    floor = ROLE_ADMIN
