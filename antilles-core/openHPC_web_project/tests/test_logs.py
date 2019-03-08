# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture
from rest_framework.status import HTTP_200_OK


@fixture(autouse=True)
def settings(settings, tmpdir):
    settings.ROOT_URLCONF = 'antilles.logs.urls'
    settings.LOG_DIR = str(tmpdir.mkdir('test'))

    return settings


def test_web_log(client, settings):
    from distutils.dir_util import mkpath
    from os import remove, path

    mkpath(settings.LOG_DIR)
    with open(
        path.join(settings.LOG_DIR, 'test.log'), 'w'
    ):
        pass

    response = client.post('/collect')
    assert response.status_code == HTTP_200_OK

    remove(path.join(settings.DOWNLOAD_DIR, response.data['name']))
