# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""


import psutil
import requests


def monitor(url, host=None, timeout=30):
    if host is None:
        import socket
        host = socket.gethostname()

    session_data = list()

    vnc_processes = filter(
        lambda process: 'Xvnc' in process.name(),
        psutil.process_iter()
    )

    for p in vnc_processes:
        cmd = p.cmdline()
        port = None

        for index, item in enumerate(cmd):
            if item == '-rfbport':
                port = int(cmd[index + 1])
                break

        session_data.append({
            'username': p.username(),
            'pid': p.pid,
            'name': host + cmd[1],
            'port': port,
            'host': host,
            'index': int(cmd[1].split(':')[1]),
        })

    requests.post(
        url,
        json={
            'host': host,
            'data': session_data
        },
        timeout=timeout
    ).raise_for_status()
