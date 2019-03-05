# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from rest_framework import serializers
from antilles.scheduler.models import Job

logger = logging.getLogger(__name__)


class JobOverViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('id', "url", "jobid", "jobname", "queue",
                  "status", "jobstatus", "qtime",
                  "starttime", "endtime", "nodescount", "cpuscount",
                  "workingdir", "type", "jobfilename", "submit_args", "charge",
                  "submiter", "walltime", "priority", "exechosts", "mail", "mailtrigger",
                  "mpi_prog", "mpi_prog_arguments", "pnodescount", "ppn", "pmem",
                  "operatestatus", "aioperatestatus", "wallduration", "billgroup", "workspace")

    def to_representation(self, obj):
        onejob = super(JobOverViewSerializer, self).to_representation(obj)
        import time
        import datetime

        def timeToUTC(times):
            return str(datetime.datetime.utcfromtimestamp(times))

        onejob["currtime"] = timeToUTC(int(time.time()))
        onejob["timezone"] = time.timezone
        onejob["starttime"] = timeToUTC(onejob["starttime"])
        onejob["endtime"] = timeToUTC(onejob["endtime"])
        onejob["qtime"] = timeToUTC(onejob["qtime"])

        return onejob


class JobDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

    def to_representation(self, obj):
        onejob = super(JobDetailSerializer, self).to_representation(obj)
        import datetime
        import time
        def timeToUTC(times):
            return str(datetime.datetime.utcfromtimestamp(times))

        onejob["currtime"] = timeToUTC(int(time.time()))
        onejob["timezone"] = time.timezone
        onejob["starttime"] = timeToUTC(onejob["starttime"])
        onejob["endtime"] = timeToUTC(onejob["endtime"])
        onejob["qtime"] = timeToUTC(onejob["qtime"])
        return onejob

    def create(self, validated_data):
        job = super(JobDetailSerializer, self).create(validated_data)
        if job.jobstatus.lower() == "c":
            job.status = "completed"
        elif job.jobstatus.lower() == "r":
            job.status = "running"
        elif job.jobstatus.lower() == "q":
            job.status = "queueing"
        elif job.jobstatus.lower() == "s":
            job.status = "suspending"
        elif job.jobstatus.lower() == "w":
            job.status = "waiting"
        elif job.jobstatus.lower() == "h":
            job.status = "holding"
        if job.operatestatus == "cancelling":
            job.status = "cancelling"
        if job.operatestatus == "creating":
            job.status = "creating"
        if job.operatestatus == "cancelled":
            job.status = "cancelled"
        if job.operatestatus == "createfailed":
            job.status = "createfailed"
        job.save()
        return job
