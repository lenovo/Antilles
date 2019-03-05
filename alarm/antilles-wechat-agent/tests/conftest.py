# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture


@fixture(scope='session', autouse=True)
def log_config():
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s-%(filename)s:%(lineno)s-%(name)s-%(message)s',
    )
