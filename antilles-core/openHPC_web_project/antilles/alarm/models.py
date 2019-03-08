# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import logging

from django.conf import settings
from django.db import models
from django.utils.timezone import localtime

from .broker import AlarmNoticeBroker


class AlarmManager(models.Manager):
    alarm_notice_mq = AlarmNoticeBroker()

    def create(self, **data):
        """
        check exists, if not create then send notices
        """
        if 'node' not in data and 'node_id' in data:
            from antilles.cluster.models import Node
            data['node'] = Node.objects.get(id=data['node_id']).hostname
        filter_dict = {
            'node': data['node'],
            'policy': data['policy'],
            'status__in': [self.model.PRESENT, self.model.CONFIRMED]
        }
        if self.filter(**filter_dict).exists():
            return None
        obj = super(AlarmManager, self).create(node=data['node'],
                                               policy=data['policy'],
                                               index=data.get('index'))
        data['create_time'] = localtime(obj.create_time)
        self.handle(data)

        return obj

    def handle(self, data):
        self.alarm_notice_mq.handle(data)


class AlarmTarget(models.Model):
    name = models.TextField(unique=True)
    phone = models.TextField(null=True)
    email = models.TextField(null=True)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': json.loads(self.phone or '[]'),
            'email': json.loads(self.email or '[]'),
        }


class Policy(models.Model):
    NOTSET = logging.NOTSET
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL
    LEVEL_CHOICES = (
        (NOTSET, 'not set'),
        (INFO, 'info'),
        (WARN, 'warn'),
        (ERROR, 'error'),
        (FATAL, 'fatal')
    )

    ON = 'ON'
    OFF = 'OFF'
    STATUS_CHOICES = (
        (ON, 'on'),
        (OFF, 'off'),
    )

    CPUSAGE = 'CPUSAGE'
    TEMP = 'TEMP'
    NETWORK = 'NETWORK'
    DISK = 'DISK'
    ELECTRIC = 'ELECTRIC'
    NODE_ACTIVE = 'NODE_ACTIVE'
    HARDWARE = 'HARDWARE'
    GPU_UTIL = 'GPU_UTIL'   # gpu utilization rate
    GPU_TEMP = 'GPU_TEMP'   # gpu temperature
    GPU_MEM = 'GPU_MEM'     # gpu memory
    METRIC_POLICY_CHOICES = (
        (CPUSAGE, 'cpusage'),
        (TEMP, 'tempature'),
        (NETWORK, 'network'),
        (DISK, 'disk'),
        (ELECTRIC, 'electric'),
        (NODE_ACTIVE, 'node_active'),
        (HARDWARE, 'hardware'),
        (GPU_UTIL, 'gpu_util'),
        (GPU_TEMP, 'gpu_temp'),
        (GPU_MEM, 'gpu_mem'),
    )

    LANGUAGE_CHOICES = settings.LANGUAGES

    metric_policy = models.CharField(
        max_length=20, choices=METRIC_POLICY_CHOICES, null=True)
    name = models.CharField(max_length=50, unique=True)
    portal = models.CharField(max_length=100)
    duration = models.DurationField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=OFF)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=NOTSET)
    nodes = models.TextField(default='all')
    creator = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
    wechat = models.BooleanField()
    sound = models.BooleanField()
    targets = models.ManyToManyField(
        AlarmTarget, blank=True, symmetrical=False
    )
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES,
                                default=settings.LANGUAGE_CODE)
    script = models.TextField(null=True)

    @classmethod
    def level_value(cls, level):
        for (n, level_value) in cls.LEVEL_CHOICES:
            if n == level:
                return level_value
        else:
            return "unknown"


class Alarm(models.Model):
    PRESENT = 'present'
    CONFIRMED = 'confirmed'
    RESOLVED = 'resolved'
    STATUS_CHOICES = (
        (PRESENT, 'present'),
        (CONFIRMED, 'confirmed'),
        (RESOLVED, 'resolved')
    )
    objects = AlarmManager()

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    node = models.TextField(db_index=True)
    index = models.IntegerField(null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PRESENT)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    comment = models.TextField()
