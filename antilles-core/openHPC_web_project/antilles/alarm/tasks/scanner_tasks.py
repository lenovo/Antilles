# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from celery import shared_task

from ..scanner.checker import AlarmCheck


@shared_task(ignore_result=True)
def cpu_scanner():
    AlarmCheck.checker("cpu")


@shared_task(ignore_result=True)
def disk_scanner():
    AlarmCheck.checker("disk")


@shared_task(ignore_result=True)
def energy_scanner():
    AlarmCheck.checker("energy")


@shared_task(ignore_result=True)
def temp_scanner():
    AlarmCheck.checker("temperature")


@shared_task(ignore_result=True)
def hardware_scanner():
    AlarmCheck.checker("hardware")


@shared_task(ignore_result=True)
def node_active():
    AlarmCheck.checker("node_active")


@shared_task(ignore_result=True)
def gpu_util_scanner():
    AlarmCheck.checker("gpu_util")


@shared_task(ignore_result=True)
def gpu_temp_scanner():
    AlarmCheck.checker("gpu_temperature")


@shared_task(ignore_result=True)
def gpu_mem_scanner():
    AlarmCheck.checker("gpu_memory")
