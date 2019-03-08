# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf.urls import url

from .views.auth import SessionView
from .views.bill import (
    BillGroupDetailView, BillGroupListView, DepositDetailView, DepositListView,
)
from .views.freeze import FreezeView
from .views.passwd import ChangePasswordView, ModifyPasswordView
from .views.user import (
    OSGroupDetailView, OSGroupListView, UnimportedUserListView, UserDetailView,
    UserExportView, UserImportDetailView, UserImportView, UserListView,
)

urlpatterns = [
    url(r'^auth/?$', SessionView.as_view()),

    url(r'^users/import/?$', UserImportView.as_view()),
    url(r'^users/import/detail/?$', UserImportDetailView.as_view()),
    url(r'^users/export/?$', UserExportView.as_view()),

    url(r'^password/?$', ChangePasswordView.as_view()),
    url(r'^users/(?P<pk>[^/]+)/password/?$',
        ModifyPasswordView.as_view()),
    url(r'^users/(?P<pk>[^/]+)/freezed/?$', FreezeView.as_view()),
    url(r'^users/unimported/?$', UnimportedUserListView.as_view()),

    url(r'^users/?$', UserListView.as_view()),
    url(r'^users/(?P<pk>[^/]+)/?$', UserDetailView.as_view()),

    url(r'^osgroups/?$', OSGroupListView.as_view()),
    url(r'^osgroups/(?P<pk>[^/]+)/?$',
        OSGroupDetailView.as_view()),

    url(r'^billgroups/?$', BillGroupListView.as_view()),
    url(r'^billgroups/(?P<pk>\w+)/?$',
        BillGroupDetailView.as_view()),

    url(r'^deposit/?$', DepositListView.as_view()),
    url(r'^deposit/(?P<pk>[0-9]+)/?$', DepositDetailView.as_view()),
]
