# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture

from antilles.user.models import User
from antilles.user.permissions import ROLE_ADMIN


@fixture(autouse=True)
def settings(settings, tmpdir):
    settings.USER_ROOT_DIR = str(tmpdir.mkdir('users_root'))
    settings.USER_SHARE_DIR = [str(tmpdir.mkdir('users_share'))]
    settings.SHARE_DIR = str(tmpdir.mkdir('share'))
    settings.LOCK_DIR = str(tmpdir.mkdir('lock'))
    settings.UPLOAD_DIR = str(tmpdir.mkdir('upload'))
    settings.DOWNLOAD_DIR = str(tmpdir.mkdir('download'))
    settings.SCRIPTS_DIR = [str(tmpdir.mkdir('scripts_dir'))]
    settings.USER_HOME_TEMP = '/etc/skel'
    settings.USE_LIBUSER = True
    settings.SCHEDULER_SOFTWARE = 'slurm'
    return settings


@fixture
def username():
    return 'antilles'


@fixture(autouse=True)
def mock_authentication(monkeypatch, username):
    from rest_framework.authentication import BaseAuthentication

    class MockAuthentication(BaseAuthentication):
        def authenticate(self, request):
            return User(username=username, role=ROLE_ADMIN), None

    monkeypatch.setattr('rest_framework.views.APIView.authentication_classes',
                        [MockAuthentication])
