# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from django.conf import settings
from django.db.models import (
    PROTECT, BooleanField, CharField, DateTimeField, ForeignKey, IntegerField,
    Model, TextField,
)
from django.forms.models import model_to_dict

from antilles.cluster.models import Node


class Job(Model):
    jobid = CharField(
        null=False, max_length=32,
        blank=True, default="", db_index=True
    )
    jobname = CharField(null=False, max_length=128, blank=True, default="")
    queue = CharField(
        null=False, max_length=128,
        blank=True, default=""
    )
    qtime = IntegerField(null=False, blank=True, default=0, db_index=True)
    starttime = IntegerField(null=False, blank=True, default=0)
    endtime = IntegerField(null=False, blank=True, default=0)
    submiter = CharField(
        null=False, max_length=32,
        blank=True, default=""
    )
    submit_args = CharField(null=False, max_length=260, blank=True, default="")
    jobstatus = CharField(
        null=False, max_length=12,
        blank=True, default=""
    )
    walltime = CharField(null=False, max_length=24, blank=True, default="")
    nodescount = IntegerField(null=False, blank=True, default=0)
    cpuscount = IntegerField(null=False, blank=True, default=0)
    priority = CharField(null=False, max_length=12, blank=True, default="")
    exechosts = CharField(null=False, max_length=512, blank=True, default="")
    type = CharField(null=False, max_length=24, blank=True, default="")
    jobfilename = CharField(null=False, max_length=260, blank=True, default="")
    workingdir = CharField(null=False, max_length=260, blank=True, default="")
    mail = CharField(null=False, max_length=260, blank=True, default="")
    mailtrigger = CharField(null=False, max_length=12, blank=True, default="")
    mpi_prog = CharField(null=False, max_length=260, blank=True, default="")
    mpi_prog_arguments = CharField(
        null=False, max_length=64, blank=True, default=""
    )
    pnodescount = IntegerField(null=False, blank=True, default=0)
    ppn = IntegerField(null=False, blank=True, default=0)
    pmem = IntegerField(null=False, blank=True, default=0)
    status = CharField(
        null=False, max_length=24,
        blank=True, default=""
    )
    isdeleted = BooleanField(null=False, blank=True, default=False)
    operatestatus = CharField(
        null=False, max_length=24, blank=True, default=""
    )
    aioperatestatus = CharField(
        null=False, max_length=24, blank=True, default=""
    )
    charge = IntegerField(null=False, blank=True, default=0)
    wallduration = IntegerField(null=False, blank=True, default=0)
    billgroup = CharField(null=False, max_length=32, blank=True, default="")
    workspace = CharField(null=False, max_length=260, blank=True, default="")
    json_body = TextField(null=False, blank=True, default="")
    gpuscount = IntegerField(null=False, blank=True, default=0)
    gpucharge = IntegerField(null=False, blank=True, default=0)
    gpusexechosts = CharField(
        null=False, max_length=512, blank=True, default=""
    )
    resumejobid = CharField(null=False, max_length=32, blank=True, default="")
    errfile = TextField(null=False, blank=True, default="")
    outfile = TextField(null=False, blank=True, default="")

    def get_absolute_url(self):
        return "/jobs/%i" % self.id

    def as_dict(self, **karg):

        import datetime
        import time

        def timeToUTC(times):
            return str(datetime.datetime.utcfromtimestamp(times))

        fields = karg.get('fields', [])
        exclude = karg.get('exclude', [])

        if karg.get('overview') is True:
            fields = [
                'id', "jobid", "jobname", "queue", "status", "jobstatus",
                "qtime", "starttime", "endtime", "nodescount", "cpuscount",
                "workingdir", "type", "jobfilename", "submit_args", "charge",
                "submiter", "walltime", "priority", "exechosts", "mail",
                "mailtrigger", "mpi_prog", "mpi_prog_arguments", "pnodescount",
                "ppn", "pmem", "operatestatus", "aioperatestatus",
                "wallduration", "billgroup", "workspace"
            ]
        data = model_to_dict(self, fields=fields, exclude=exclude)

        # data["url"] = self.get_absolute_url()
        data["currtime"] = timeToUTC(int(time.time()))
        data["timezone"] = time.timezone
        data["starttime"] = timeToUTC(data["starttime"])
        data["endtime"] = timeToUTC(data["endtime"])
        data["qtime"] = timeToUTC(data["qtime"])

        return data

    def save(self, *args, **kwargs):

        if not self.id:
            job_status_mapping = {
                "c": "completed",
                "r": "running",
                "q": "queueing",
                "s": "suspending",
                "w": "waiting",
                "h": "holding"
            }

            op_status_mapping = {
                "cancelling": "cancelling",
                "creating": "creating",
                "cancelled": "cancelled",
                "createfailed": "createfailed"
            }

            if self.jobstatus.lower():
                self.status = job_status_mapping[self.jobstatus.lower()]
            if self.operatestatus:
                self.status = op_status_mapping[self.operatestatus]

        super(Job, self).save(*args, **kwargs)


class RunningJob(Model):
    job = ForeignKey('Job', blank=False, on_delete=PROTECT)
    node = ForeignKey(Node, blank=False, on_delete=PROTECT)
    core_num = IntegerField(null=False, blank=False)
    gpu_num = IntegerField(null=False, blank=False)


# used for online real time log
class JobConsole(Model):
    job_run_id = CharField(null=False, max_length=32)
    console_server = CharField(default="", max_length=64)


# Add New Job Template Table
class JobTemplate(Model):
    name = CharField(null=False, max_length=32)
    logo = TextField()
    desc = CharField(max_length=500, default='')
    parameters_json = TextField(null=False)
    template_file = TextField(null=False)
    type = CharField(max_length=32, default='')
    category = CharField(max_length=100, default='')
    user_id = IntegerField()
    scheduler = CharField(max_length=32, default='')
    feature_code = CharField(max_length=32, default='')
    create_time = DateTimeField(auto_now_add=True)
    update_time = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'user_id')

    def as_dict(self, **kwargs):
        data = model_to_dict(self,
                             fields=kwargs.get('fields', []),
                             exclude=kwargs.get('exclude', []))
        return data
