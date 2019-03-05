# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.status import HTTP_400_BAD_REQUEST

from antilles.user.models import BillGroup, User

from .exceptions import UserAlreadyExistsException, UsermanagerException

logger = logging.getLogger(__name__)


class BillGrouopNotExists(UsermanagerException):
    status_code = HTTP_400_BAD_REQUEST
    message = 'Billgroup not exists.'
    errid = 2023


class DeleteNoteAllowException(UsermanagerException):
    message = 'Unable to delete object.'
    status = HTTP_400_BAD_REQUEST
    errid = 2006


class DatabaseManager(object):
    def __getattr__(self, operating):
        return DatabasePoerating(operating)


class DatabasePoerating(object):
    '''proxy DatabaseOperatings methods for wrap exception handle'''

    def __init__(self, operating):
        self.operating = operating

    def __call__(self, *args, **karg):
        operatings = DatabaseOperatings()
        func = getattr(operatings, self.operating)
        try:
            return func(*args, **karg)
        except ProtectedError:
            raise DeleteNoteAllowException
        except IntegrityError:
            raise UserAlreadyExistsException
        except ObjectDoesNotExist as e:
            msg = getattr(e, 'message', 'Object not exists')
            raise NotFound(detail=msg)
        except BillGrouopNotExists:
            raise BillGrouopNotExists
        except Exception as e:
            logger.exception('user database {}'.format(func.__name__))
            raise UsermanagerException


class DatabaseOperatings(object):
    '''manage user data in database'''

    def add_user(self, username, bill_group, role=None,
                 email=None, first_name=None, last_name=None):
        if isinstance(bill_group, int):
            bill_group = BillGroup.objects.get(id=bill_group)
        role = User.ROLES['user'] if role is None else role
        if isinstance(role, basestring):
            role = User.ROLES[role]

        user = User.objects.create(
            username=username,
            role=role,
            bill_group=bill_group,
            email=email,
            first_name=first_name,
            last_name=last_name,
            last_operation_time=timezone.now(),
        )

        return user.as_dict()

    def update_user(self, id, data):
        user = User.objects.get(id=id)
        if 'username' in data:
            raise PermissionDenied(detail='can not modify username')
        for k, v in data.items():
            if k == 'bill_group':
                try:
                    user.bill_group = BillGroup.objects.get(id=v)
                except Exception:
                    raise BillGrouopNotExists
            elif k == 'role':
                user.role = User.ROLES[v]
            else:
                setattr(user, k, v)
        user.last_operation_time = timezone.now()
        user.save()
        return user.as_dict()

    def remove_user(self, id):
        try:
            return User.objects.get(id=id).delete()
        except ObjectDoesNotExist:
            return False

    def get_user(self, pk):
        try:
            return User.objects.get(id=int(pk)).as_dict()
        except ValueError:
            return User.objects.get(username=pk).as_dict()

    def is_last_admin(self, username):
        user = self.get_user(username)
        if user['role'] == 'admin' and \
                User.objects.filter(role=User.ROLES['admin']).count() == 1:
            return True
        return False
