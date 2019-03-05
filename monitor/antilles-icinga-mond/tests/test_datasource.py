# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from pytest import fixture

from requests import Response, packages

packages.urllib3.disable_warnings()


@fixture
def results():
    import json
    r = Response()
    r._content = json.dumps({
        "results": [{
            "attrs": {
                "display_name": "antilles-demo",
                "host_name": "head.hpc.com",
                "last_check_result": {
                    "active": True,
                    "check_source": "head.hpc.com",
                    "command": ["/usr/lib64/nagios/plugins/antilles-monitoring", "-a"],
                    "execution_end": 1533801954.1090741158,
                    "execution_start": 1533801951.8103458881,
                    "exit_status": 0,
                    "output": "Ok - Cpu util\nOk - Cpu Nums\nOk - Cpu load\nOk - Memory used\nOk - Memory util\nOk - Memory total\nOk - Gpu mem pct\nOk - Gpu mem pct\nOk - Gpu temp\nOk - Gpu temp\nOk - Gpu process\nOk - Gpu process\nOk - Gpu util\nOk - Gpu util\nOk - Gpu Nums\nOk - Gpu use nums\nOk - Gpu type\nOk - Gpu type\nOk - Disk total\nOk - Disk used\nOk - Disk util\nOk - Network in\nOk - Network out",
                    "performance_data": ["cpu-util=2.9%", "cpu-num=48", "cpu-load=0.68", "memory-used=9319076KB",
                                         "memory-util=2.4%", "memory-total=395704824KB", "gpu-memory-util_0=0.0%",
                                         "gpu-memory-util_1=20.0%", "gpu-temp_0=31", "gpu-temp_1=65", "gpu-process_0=0",
                                         "gpu-process_1=1", "gpu-util_0=0.0%", "gpu-util_1=5.0%", "gpu-num=2",
                                         "gpu-used-num=1;", "'gpu-type_0[Tesla P100-PCIE-16GB]'=0",
                                         "'gpu-type_1[Tesla P100-PCIE-32GB]'=1", "disk-total=14320GB",
                                         "disk-used=3231GB", "disk-util=22.6%", "network-in=810B", "network-out=2483B"],
                    "schedule_end": 1533801954.1093270779,
                    "schedule_start": 1533801951.8101119995,
                    "state": 0,
                    "type": "CheckResult",
                    "vars_after": {
                        "attempt": 1,
                        "reachable": True,
                        "state": 0,
                        "state_type": 1
                    },
                    "vars_before": {
                        "attempt": 1,
                        "reachable": True,
                        "state": 0,
                        "state_type": 1
                    }
                },
                "state": 0
            },
            "joins": {},
            "meta": {},
            "name": "head!antilles-demo",
            "type": "Service"
        }]
    })
    return r


def test_parse(mocker, results):
    mocker.patch(
        "requests.post",
        return_value=results
    )

    from antilles.mond.icinga.datasource import DataSource
    ds = DataSource(
        host="127.0.0.1",
        port=5665,
        user="root",
        password="Passw0rd",
        service="antilles-demo",
        domain_filter=[".hpc.com"]
    )

    for d in ds.parse():
        assert isinstance(d, dict)
        assert "host" in d
        assert "value" in d
        assert "unit" in d
        assert "index" in d
        assert "service" in d

        assert d["host"] == "head"
        if "cpu-util" == d["service"]:
            assert d["value"] == 2.9
            assert d["unit"] == "percent"
            assert d["index"] is None
        elif "cpu-num" == d["service"]:
            assert d["value"] == 48.0
            assert d["unit"] == ""
            assert d["index"] is None
        elif "cpu-load" == d["service"]:
            assert d["value"] == 0.68
            assert d["unit"] == ""
            assert d["index"] is None
        elif "memory-used" == d["service"]:
            assert d["value"] == 9319076 * 1024.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "memory-util" == d["service"]:
            assert d["value"] == 2.4
            assert d["unit"] == "percent"
            assert d["index"] is None
        elif "memory-total" == d["service"]:
            assert d["value"] == 395704824 * 1024.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "disk-total" == d["service"]:
            assert d["value"] == 14320 * 1024.0 * 1024.0 * 1024.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "disk-used" == d["service"]:
            assert d["value"] == 3231 * 1024.0 * 1024.0 * 1024.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "disk-util" == d["service"]:
            assert d["value"] == 22.6
            assert d["unit"] == "percent"
            assert d["index"] is None
        elif "network-in" == d["service"]:
            assert d["value"] == 810.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "network-out" == d["service"]:
            assert d["value"] == 2483.0
            assert d["unit"] == "bytes"
            assert d["index"] is None
        elif "gpu-num" == d["service"]:
            assert d["value"] == 2.0
            assert d["unit"] == ""
            assert d["index"] is None
        elif "gpu-used-num" == d["service"]:
            assert d["value"] == 1.0
            assert d["unit"] == ""
            assert d["index"] is None
        elif "gpu-memory-util" == d["service"]:
            assert d["unit"] == "percent"
            if d["index"] == 0:
                assert d["value"] == 0.0
            elif d["index"] == 1:
                assert d["value"] == 20.0
        elif "gpu-temp" == d["service"]:
            assert d["unit"] == ""
            if d["index"] == 0:
                assert d["value"] == 31.0
            elif d["index"] == 1:
                assert d["value"] == 65.0
        elif "gpu-process" == d["service"]:
            assert d["unit"] == ""
            if d["index"] == 0:
                assert d["value"] == 0.0
            elif d["index"] == 1:
                assert d["value"] == 1.0
        elif "gpu-util" == d["service"]:
            assert d["unit"] == "percent"
            if d["index"] == 0:
                assert d["value"] == 0.0
            elif d["index"] == 1:
                assert d["value"] == 5.0
        elif "gpu-type" == d["service"]:
            assert d["unit"] == ""
            if d["index"] == 0:
                assert d["value"] == "Tesla P100-PCIE-16GB"
            elif d["index"] == 1:
                assert d["value"] == "Tesla P100-PCIE-32GB"
