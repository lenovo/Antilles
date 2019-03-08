# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import re

from requests import packages, post

from .exceptions import InvalidPerformanceData

packages.urllib3.disable_warnings()


# Service State Define in Icinga2
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


class DataSource(object):
    def __init__(
            self, host, port, user, password, service,
            attrs="",
            api_v="v1",
            domain_filter=list(),
            timeout=30
    ):
        self.url = "https://{0}:{1}/{2}/objects/services".format(
            host, port, api_v
        )
        self.headers = {
            "Accept": "application/json",
            "X-HTTP-Method-Override": "GET"
        }
        self.auth = (user, password)
        self.service = service
        self.domain_filter = domain_filter
        self.attrs = [
            "display_name",
            "host_name",
            "last_check_result",
            "state"
        ] + attrs.split()
        self.data = {
            "attrs": self.attrs
        }
        self.timeout = timeout
        self.rex_value = re.compile(r'[^0-9\+-\.e]')

    def _parseWarnCritMinMaxToken(self, tokens, index):
        if len(tokens) > index \
                and tokens[index] != "U" \
                and tokens[index] != "" \
                and self.rex_value.search(tokens[index]) is None:
            return float(tokens[index])
        else:
            return ""

    def _perfDataValue(self, **kwargs):
        perf = dict()
        perf["label"] = kwargs.get("label", "")
        perf["value"] = kwargs.get("value", None)
        perf["counter"] = kwargs.get("counter", False)
        perf["unit"] = kwargs.get("unit", "")
        perf["warn"] = kwargs.get("warn", None)
        perf["crit"] = kwargs.get("crit", None)
        perf["min"] = kwargs.get("min", None)
        perf["max"] = kwargs.get("max", None)
        perf["type"] = "PerfdataValue"

        return perf

    # Format of perfdata:
    # 'label'=value[UOM];[warn];[crit];[min];[max]
    def _parse_performance_data(self, perfdata):
        if "=" not in perfdata:
            raise InvalidPerformanceData(perfdata)

        perfs = perfdata.split("=")
        label = perfs[0]

        if len(label) > 2 and label.startswith("'") and label.endswith("'"):
            label = label[1:-1]

        values = perfs[1].split(";")
        valueStr = values[0].strip()
        tokens = values[1:]
        unit = ""
        pattern = self.rex_value.search(valueStr)
        if pattern:
            value = float(valueStr[:pattern.start()])
            unit = valueStr[pattern.start():]
        else:
            value = float(valueStr)

        unit = unit.lower()

        base = 1.0
        counter = False

        if unit == "us":
            base /= 1000.0 * 1000.0
            unit = "seconds"
        elif unit == "ms":
            base /= 1000.0
            unit = "seconds"
        elif unit == "s":
            unit = "seconds"
        elif unit == "tb":
            base *= 1024.0 * 1024.0 * 1024.0 * 1024.0
            unit = "bytes"
        elif unit == "gb":
            base *= 1024.0 * 1024.0 * 1024.0
            unit = "bytes"
        elif unit == "mb":
            base *= 1024.0 * 1024.0
            unit = "bytes"
        elif unit == "kb":
            base *= 1024.0
            unit = "bytes"
        elif unit == "b":
            unit = "bytes"
        elif unit == "%":
            unit = "percent"
        elif unit == "c":
            counter = True
            unit = ""
        elif unit != "":
            raise InvalidPerformanceData(perfdata)

        warn = self._parseWarnCritMinMaxToken(tokens, 0)
        crit = self._parseWarnCritMinMaxToken(tokens, 1)
        min = self._parseWarnCritMinMaxToken(tokens, 2)
        max = self._parseWarnCritMinMaxToken(tokens, 3)

        value *= base

        if warn != "":
            warn *= base
        if crit != "":
            crit *= base
        if min != "":
            min *= base
        if max != "":
            max *= base

        return self._perfDataValue(
            label=label,
            value=value,
            counter=counter,
            unit=unit,
            warn=warn,
            crit=crit,
            min=min,
            max=max
        )

    def _filterDomain(self, host):
        if host == "":
            return host
        for domain in self.domain_filter:
            if host.endswith(domain):
                return host[:-len(domain)]
        else:
            return host

    def _output_format(self, **kwargs):
        output = dict()
        perf = kwargs.get("performance_data", None)
        if not perf:
            return output
        output["host"] = kwargs.get("host", "")
        output["value"] = perf["value"]
        output["unit"] = perf["unit"]
        output["index"] = None
        label = perf["label"]
        output["service"] = label

        if label.startswith("gpu-type"):
            output["service"] = "gpu-type"
            output["index"] = int(perf["value"])
            pos_s, pos_e = (label.index("[") + 1, label.rindex("]"))
            output["value"] = label[pos_s:pos_e]
        elif label.startswith("gpu") and not label.endswith("-num"):
            service, index = label.split("_")
            output["service"] = service
            output["index"] = int(index)

        return output

    def parse(self):
        res = post(
            url=self.url,
            headers=self.headers,
            auth=self.auth,
            data=json.dumps(self.data),
            verify=False,
            timeout=self.timeout
        )

        for result in res.json().get("results", list()):
            attrs = result.get("attrs", dict())
            if attrs.get("display_name", "") != self.service:
                continue
            if attrs.get("state", 0) >= CRITICAL:
                continue
            host = self._filterDomain(attrs.get("host_name", ""))
            last_check_result = attrs.get("last_check_result", dict())
            perfdatas = last_check_result.get("performance_data", list())
            for perf in perfdatas:
                output = self._output_format(
                    host=host,
                    performance_data=self._parse_performance_data(perf)
                )
                if not output:
                    continue
                yield output
