# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture


@fixture(autouse=True)
def settings(settings, tmpdir):
    settings.ROOT_URLCONF = 'antilles.cluster.urls'

    settings.CONFLUENT_USER = 'antilles'
    settings.CONFLUENT_PASS = 'Passw0rd'
    settings.CONFLUENT_PORT = 4005

    return settings
