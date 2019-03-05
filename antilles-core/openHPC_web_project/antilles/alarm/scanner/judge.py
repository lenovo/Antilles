# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import pandas

from antilles.alarm.models import Policy

from .base import Base

PERCENTAGE = [Policy.CPUSAGE,
              Policy.DISK,
              Policy.GPU_UTIL,
              Policy.GPU_MEM]


class Judge(Base):
    def __init__(self, datas, policy):
        super(Judge, self).__init__(policy)
        self._datas = datas

    @property
    def _threshold(self):
        if self._policy.metric_policy in PERCENTAGE:
            self._val *= 100.0
            return int(self._val)
        else:
            return int(self._val)

    def _gen_alarm_list(self, targets):
        alarm_list = []
        alarm_data = {}
        if "index" in targets:
            for target in targets.loc[:, ['host', 'index']].values:
                alarm_data["node"] = target[0]
                alarm_data["index"] = target[1]
                alarm_list.append(alarm_data.copy())
        else:
            for target in targets.loc[:, ['host']].values:
                alarm_data["node"] = target[0]
                alarm_list.append(alarm_data.copy())
        return alarm_list

    def compare(self):
        alarm_data = {}
        alarm_list = []
        df = pandas.DataFrame(self._datas)
        if "val" in df.columns:
            if self._aggregate == "max":
                targets = df.ix[df.val <= self._threshold, :]
                alarm_list = self._gen_alarm_list(targets)
            elif self._aggregate == "min":
                targets = df.ix[df.val >= self._threshold, :]
                alarm_list = self._gen_alarm_list(targets)
            else:
                if self._policy.metric_policy == Policy.NODE_ACTIVE \
                        or self._policy.metric_policy == Policy.HARDWARE:
                    if "host" in df.columns:
                        targets = df.loc[:, ['host', 'val']].drop_duplicates()
                        all_nodes = set(targets['host'].values)
                        exclude_nods = set(targets.loc[
                                               targets['val']
                                           .isin(['on', 'ok', 'null'])
                                           ]['host'].values
                                           )

                        for target in all_nodes - exclude_nods:
                            alarm_data["node"] = target
                            alarm_list.append(alarm_data.copy())
        return alarm_list
