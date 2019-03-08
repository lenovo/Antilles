# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from antilles.cluster.managers import power


def test_start_up_device(mocker):
    mock = mocker.patch('antilles.cluster.managers.power.requests')
    node = mocker.MagicMock()
    power.startup_device(node, 'bootmode', 'nextdevice', 'persistent')

    assert mock.post.call_count == 2


def test_start_up_device_without_nextdevice(mocker):
    mock = mocker.patch('antilles.cluster.managers.power.requests')
    node = mocker.MagicMock()
    power.startup_device(node, 'bootmode', None, 'persistent')

    assert mock.post.call_count == 1


def test_shutdown_device(mocker):
    mock = mocker.patch('antilles.cluster.managers.power.requests')
    node = mocker.MagicMock()
    power.shutdown_device(node)

    mock.put.assert_called_once()
