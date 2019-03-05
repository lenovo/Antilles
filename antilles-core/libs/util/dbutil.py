# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
import time
import os

from antilles.cluster.models import Node
from antilles.scheduler.models import Job, RunningJob
from antilles.user.models import BillGroup, User

logger = logging.getLogger(__name__)

EXCHANGE_RATE = 3600
SECONDS_OF_HOUR = 3600


class Recevier(object):
    @staticmethod
    def updatestatus(job):
        # job.status decides user joblist layout

        # jobstatus get from scheduler
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
        elif job.jobstatus.lower() == "cancelled":
            job.status = "cancelled"

        # operatestatus get from request
        if job.operatestatus == "cancelling":
            job.status = "cancelling"
        elif job.operatestatus == "creating":
            job.status = "creating"
        elif job.operatestatus == "cancelled":
            job.status = "cancelled"
        elif job.operatestatus == "createfailed":
            job.status = "createfailed"
        elif job.operatestatus == "rerunfailed":
            job.status = "rerunfailed"

    @staticmethod
    def charge_job(job):
        try:
            wallduration = job.endtime - job.starttime
            usedalltime = job.cpuscount * wallduration
            if usedalltime < 0:
                usedalltime = 0
            job.charge = usedalltime
            job.gpucharge = job.gpuscount * wallduration
            job.wallduration = wallduration
            billgroup = BillGroup.objects.get(name=job.billgroup)
            billgroup.balance -= round(usedalltime * billgroup.charge_rate / SECONDS_OF_HOUR, 2)
            billgroup.used_time += usedalltime
            billgroup.used_credits += round(usedalltime * billgroup.charge_rate / SECONDS_OF_HOUR, 2)
            billgroup.save()
        except:
            pass

    @classmethod
    def create_job_resp(cls, **kwargs):
        id = kwargs.get("id")
        op_result = kwargs.get("op_result")
        job = Job.objects.get(id=id)
        if op_result == "success":
            job.jobid = kwargs.get("jobid")
            job.jobstatus = kwargs.get("jobstatus", "").upper()
            if kwargs.get("jobname") != "":
                job.jobname = kwargs.get("jobname")
            if kwargs.get("queue") != "":
                job.queue = kwargs.get("queue")
            if kwargs.get("workingdir") != "":
                job.workingdir = kwargs.get("workingdir")
            if kwargs.get("jobfilename") != "":
                job.jobfilename = kwargs.get("jobfilename")
            job.operatestatus = kwargs.get("operatestatus")
            Recevier.updatestatus(job)
            job.save()
        else:
            job.jobid = kwargs.get("jobid", "")
            job.jobstatus = kwargs.get("jobstatus", "").upper()
            job.operatestatus = kwargs.get("operatestatus")
            job.endtime = kwargs.get("endtime")
            Recevier.updatestatus(job)
            job.save()

    @classmethod
    def update_job(cls, **kwargs):
        import json
        jobid = kwargs.get("jobid")
        job = None
        hosts_cpus = {}
        hosts_gpus = {}
        try:
            job = Job.objects.get(jobid=jobid)
            if job.jobstatus.lower() == "c":
                # RunningJob.objects.filter(job__jobid__contains=jobid).delete()
                RunningJob.objects.filter(job__jobid=jobid).delete()
                if kwargs.get("jobstatus") and kwargs.get("jobstatus").lower() == "c":
                    return
                job.operatestatus = "created"
            if job.jobstatus.upper() == kwargs.get("jobstatus", "").upper():
                return
            job.jobstatus = kwargs.get("jobstatus", "").upper()
        except Job.DoesNotExist:
            if kwargs.get("type") != "cmd":
                return
            submiter = kwargs.get("submiter")
            workspace = None
            billgroup = None
            try:
                usermodel = User.objects.get(username=submiter)
                workspace = usermodel.workspace
                if workspace[-1] == '/' or workspace[-1] == "\\":
                    workspace = workspace[0:-1]
                billgroup = usermodel.bill_group.name
            except:
                # if submitter is in antilles database, record the job info only.
                logger.info("Job submitter %s is not a registered user in database." % submiter)
                pass
            job = Job.objects.create()
            job.type = "cmd"
            job.submiter = submiter
            if billgroup:
                job.billgroup = billgroup
            if workspace:
                job.workspace = workspace
            job.workingdir = "MyFolder"
            if kwargs.get("qtime") > 0:
                job.qtime = kwargs.get("qtime")
            else:
                job.qtime = time.time()
            job.jobid = kwargs.get("jobid")
            job.queue = kwargs.get("queue")
            job.jobname = kwargs.get("jobname")
            if os.path.exists(kwargs.get('submit_args')):
                job.jobfilename = os.path.join('MyFolder/',
                                               os.path.relpath(kwargs.get('submit_args'), start=workspace))
            job.operatestatus = "created"
            job.jobstatus = kwargs.get("jobstatus")
            
        # New add errfile and outfile field
        job.errfile = os.path.abspath(kwargs.get('errfile'))
        job.outfile = os.path.abspath(kwargs.get('errfile'))


        if kwargs.get("starttime") != 0 and job.jobstatus.lower() != 'q':
            job.starttime = kwargs.get("starttime")
        if kwargs.get("endtime") > 0 \
                and (job.jobstatus.lower() == 'c'
                        or job.jobstatus.lower() == 'cancelled'):
            job.endtime = kwargs.get("endtime")
        if kwargs.get("walltime") != "":
            job.walltime = kwargs.get("walltime")
        if kwargs.get("nodescount") > 0:
            job.nodescount = kwargs.get("nodescount")
        if kwargs.get("cpuscount") > 0:
            job.cpuscount = kwargs.get("cpuscount")
        if kwargs.get("gpuscount") > 0:
            job.gpuscount = kwargs.get("gpuscount")
        if kwargs.get("priority") != "":
            job.priority = kwargs.get("priority")
        if kwargs.get("hosts_cpus") != "":
            try:
                hosts_cpus = json.loads(kwargs.get("hosts_cpus"))
                exechosts = '+'.join([k + "*" + str(v) for (k, v) in hosts_cpus.items()])
            except:
                exechosts = ""
            job.exechosts = exechosts[:500]
        if kwargs.get("hosts_gpus") != "":
            try:
                hosts_gpus = json.loads(kwargs.get("hosts_gpus"))
                gpusexechosts = '+'.join([k + "*" + str(v) for (k, v) in hosts_gpus.items()])
            except:
                gpusexechosts = ""
            job.gpusexechosts = gpusexechosts[:500]
        if kwargs.get("submit_args") != "":
            job.submit_args = kwargs.get("submit_args")
            if len(job.submit_args) > 250:
                job.submit_args = job.submit_args[:250]
        if job.jobstatus.lower() == "c" \
                or job.jobstatus.lower() == "cancelled":
            if job.starttime == 0:
                job.starttime = time.time()
            if job.endtime == 0:
                job.endtime = time.time()
            if job.starttime > job.endtime:
                job.endtime = job.starttime
            if job.jobstatus.lower() == "c":
                Recevier.charge_job(job)
        elif job.jobstatus.lower() == "r":
            if job.endtime > 0:
                job.endtime = 0
        else:
            if job.starttime > 0:
                job.starttime = 0
            if job.endtime > 0:
                job.endtime = 0
        Recevier.updatestatus(job)
        job.save()
        if job.jobstatus.lower() == "r":
            for hostname, cpu_num in hosts_cpus.items():
                try:
                    node = Node.objects.get(hostname=str(hostname))
                    RunningJob.objects.update_or_create(node=node, job=job,
                                                        core_num=int(cpu_num), gpu_num =0)
                except:
                    logger.exception("Update running job failed.")
                    continue
            for hostname, gpu_num in hosts_gpus.items():
                try:
                    node = Node.objects.get(hostname=str(hostname))
                    RunningJob.objects.filter(node=node, job=job).update(gpu_num=int(gpu_num))
                except:
                    logger.exception("Update running job failed.")
                    continue
        else:
            # RunningJob.objects.filter(job__jobid__contains=jobid).delete()
            RunningJob.objects.filter(job__jobid=jobid).delete()

    @classmethod
    def cancel_job_resp(cls, **kwargs):
        id = kwargs.get("id")
        op_result = kwargs.get("op_result")
        job = Job.objects.get(id=id)
        if op_result == "success":
            job.operatestatus = kwargs.get("operatestatus")
            job.endtime = kwargs.get("endtime")
            Recevier.updatestatus(job)
            job.save()
            # delete running job
            # RunningJob.objects.filter(job__id__contains=id).delete()
            RunningJob.objects.filter(job__id=id).delete()
        else:
            job.operatestatus = kwargs.get("operatestatus")
            Recevier.updatestatus(job)
            job.save()

    @classmethod
    def clean_job_dirty_data(cls, **kwargs):
        import time
        currtime = time.time()
        jobs = Job.objects.exclude(jobstatus="C")
        jobs.update(
            jobstatus="C",
            operatestatus="cancelled",
            status="cancelled",
            starttime=currtime,
            endtime=currtime
        )
        RunningJob.objects.all().delete()

    @classmethod
    def clear_jobs_by_jobid(cls, **kwargs):
        import time
        currtime = time.time()
        jobids = kwargs.get("jobids")
        if jobids:
            jobs = Job.objects.filter(jobid__in=jobids).exclude(jobstatus="C")
            jobs.update(
                jobstatus="C",
                operatestatus="cancelled",
                status="cancelled",
                starttime=currtime,
                endtime=currtime
            )
            RunningJob.objects.filter(job__jobid__in=jobids).delete()


class DBUtil(object):
    def __init__(self):
        self.Recevier = Recevier

    def invoke_save(self, msg):
        logger.debug('saved db directly:%s ' % (msg, ))
        try:
            call_method = msg["method"]
            args = msg["args"]
            callback_method = getattr(self.Recevier, call_method)
            callback_method(**args)
        except:
            logger.exception(
                "error occured when saving db directly message: %s" % msg)

