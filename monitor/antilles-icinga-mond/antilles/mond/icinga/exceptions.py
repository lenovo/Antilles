# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""


class ConfigFileNotExist(Exception):
    def __init__(self, path):
        self.err = "Config file {0} is not exist".format(path)
        Exception.__init__(self, self.err)


class InvalidPerformanceData(Exception):
    def __init__(self, perfdata):
        self.err = "Invalid performance data value: {0}".format(perfdata)
        Exception.__init__(self, self.err)
