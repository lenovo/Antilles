# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from celery import shared_task
from django.core.cache import cache
from django.db import IntegrityError, transaction

from antilles.cluster.models import Gpu, Node

logger = logging.getLogger(__name__)

_NODE_SQL = """\
SELECT LAST(value) as value FROM node_disk_total
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_disk
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_mem_total
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_mem
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_network_in
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_network_out
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_cpu_num
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_cpu
WHERE time > now() - 1m GROUP BY host;
SELECT LAST(value) as value FROM node_active
WHERE time > now() - 1m GROUP BY host;
"""

_GPU_SQL = """\
SELECT LAST(value) as value FROM node_gpu_mem_pct
WHERE time > now() - 1m GROUP BY host, index;
SELECT LAST(value) as value FROM node_gpu_process
WHERE time > now() - 1m GROUP BY host, index;
SELECT LAST(value) as value FROM node_gpu_temp
WHERE time > now() - 1m GROUP BY host, index;
SELECT LAST(value) as value FROM node_gpu_type
WHERE time > now() - 1m GROUP BY host, index;
SELECT LAST(value) as value FROM node_gpu_util
WHERE time > now() - 1m GROUP BY host, index;
"""

field_mapping = {
    "node_gpu_mem_pct": "memory_util",
    "node_gpu_process": "occupation",
    "node_gpu_temp": "temperature",
    "node_gpu_type": "type",
    "node_gpu_util": "util",
    "node_active": "power_status",
    "node_cpu": "cpu_util",
    "node_disk_total": "disk_total",
    "node_disk": "disk_used",
    "node_mem_total": "memory_total",
    "node_mem": "memory_used",
    "node_network_in": "network_in",
    "node_network_out": "network_out",
    "node_cpu_num": "cpu_total"
}

type_mapping = {
    "node_gpu_mem_pct": int,
    "node_gpu_process": bool,
    "node_gpu_temp": int,
    "node_gpu_type": str,
    "node_gpu_util": int,
    "node_cpu": float,
    "node_disk_total": float,
    "node_disk": float,
    "node_mem_total": float,
    "node_mem": float,
    "node_network_in": float,
    "node_network_out": float,
    "node_cpu_num": int,
    "node_active": bool
}


@shared_task(ignore_result=True)
def node_summaries():
    # node_caches format: {host:{memory_util: 12, occupation: True, ...}, }
    node_caches = dict()
    results = cache.get(_NODE_SQL)

    for result in results:
        for k, v in result.items():
            host = k[1]["host"]
            field = k[0]
            origin_val = list(v)[0]["value"]
            if "node_active" == field:
                origin_val = (origin_val.lower() == "on")
            val = type_mapping[field](origin_val)
            if host not in node_caches:
                node_caches[host] = dict()
            node = node_caches[host]
            node.update({field_mapping[field]: val})
    try:
        reset_state = {
            "power_status": False,
            "cpu_util": 0.0,
            "memory_used": 0.0,
            "network_in": 0.0,
            "network_out": 0.0
        }
        with transaction.atomic():
            for k_host, k_value in node_caches.items():
                if "power_status" not in k_value \
                        or k_value["power_status"] is False:
                    del node_caches[k_host]
                    logger.info(
                        "Host %s is off on confluent, "
                        "so discard its data from ganglia", k_host
                    )
                    continue
                Node.objects.filter(hostname=k_host).update(**k_value)

            Node.objects.exclude(
                hostname__in=node_caches.keys()
            ).update(**reset_state)
    except IntegrityError:
        logger.exception("Failed for node summaries")


@shared_task(ignore_result=True)
def node_gpu_summaries():
    # gpu_caches format:
    # {host:{gpu_idx: {memory_util: 12, occupation: True, ...}, }}
    gpu_caches = dict()
    results = cache.get(_GPU_SQL)

    for result in results:
        for k, v in result.items():
            host = k[1]["host"]
            field = k[0]
            index = int(k[1]["index"])
            val = type_mapping[field](list(v)[0]["value"])

            gpu_caches[host] = gpus = gpu_caches.get(host, dict())
            gpus[index] = gpu = gpus.get(index, dict())
            gpu.update({field_mapping[field]: val})

    try:
        with transaction.atomic():
            update_ids = []
            for k_host, v_gpus in gpu_caches.iteritems():
                try:
                    node = Node.objects.get(hostname=k_host)
                except Node.DoesNotExist:
                    continue
                for k_idx, v_gpu in v_gpus.iteritems():
                    gpu, ret = node.gpu.update_or_create(
                        index=k_idx,
                        defaults=v_gpu
                    )
                    update_ids.append(gpu.id)
            Gpu.objects.exclude(id__in=update_ids).delete()
    except IntegrityError:
        logger.exception("Failed for node gpu summaries")
