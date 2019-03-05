# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import dbm
from datetime import datetime

from .exception import ReachDailyLimit


class Counter(object):
    def __init__(self, dbpath):
        self.db = dbm.open(dbpath, 'c')

    @property
    def key(self):
        return datetime.now().strftime('%x')

    @property
    def value(self):
        return int(self.db.get(self.key, 0))

    def __iadd__(self, value):
        key = self.key
        current = int(self.db.get(key, 0))
        current += value
        self.db[key] = str(current)
        return self

    def check_limit(self, limit):
        if self.value > limit:
            raise ReachDailyLimit(
                description='sms reach daily limit: {}'.format(limit)
            )


def send_sms(phone, serial_port, data):
    from ._pysms import Modem
    with Modem(str(serial_port)) as modem:
        modem.send_msg(str(phone), str(data))
