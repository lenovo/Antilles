# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from libs.datamodule.jobdef import Job, CommonJob
from libs.util.jobutil import JobUtil
from libs.util.dbutil import DBUtil
from libs.job.job_manager import JobManager
from antilles.scheduler.models import Job as Job_m
import traceback
import logging
import json
import threading
from itertools import chain
from django.conf import settings


g_mq_create_job_event = threading.Event()

g_jobop_lock = threading.RLock()
g_ui_jobs = {}

logger = logging.getLogger(__name__)


class JobMqOperations():
    @classmethod
    def create_job(cls, args):
        logger.debug("create_job entry")
        import time
        id = args["id"]
        ret, job = JobMqOperations._create_job_op(args)
        if ret:
            logger.debug("create_job success")
            retdata = {}
            retdata["method"] = "create_job_resp"
            args_dict = json.loads(job.tojson())
            args_dict["id"] = id
            args_dict["op_result"] = "success"
            args_dict["operatestatus"] = "created"
            args_dict["jobstatus"] = "Q"
            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)
            g_mq_create_job_event.set()
        else:
            logger.error("create_job failed")
            retdata = {}
            retdata["method"] = "create_job_resp"
            args_dict = {}
            args_dict["id"] = id
            args_dict["op_result"] = "failed"
            args_dict["operatestatus"] = "createfailed"
            args_dict["jobstatus"] = "C"
            args_dict["endtime"] = int(time.time())
            jobid = ""
            if job is not None and job.jobid != "":
                jobid = job.jobid

            args_dict["jobid"] = jobid
            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)

    @classmethod
    def rerun_job(cls, args):
        logger.debug("rerun_job entry")
        import time
        id = args["id"]
        ret, job = JobMqOperations._rerun_job_op(args)
        if ret:
            logger.debug("rerun_job success")
            retdata = {}
            retdata["method"] = "create_job_resp"
            args_dict = json.loads(job.tojson())
            args_dict["id"] = id
            args_dict["op_result"] = "success"
            args_dict["operatestatus"] = "created"
            args_dict["jobstatus"] = "Q"
            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)
            g_mq_create_job_event.set()
        else:
            logger.error("rerun_job failed")
            retdata = {}
            retdata["method"] = "create_job_resp"
            args_dict = {}
            args_dict["id"] = id
            args_dict["op_result"] = "failed"
            args_dict["operatestatus"] = "createfailed"
            args_dict["jobstatus"] = "C"
            args_dict["endtime"] = int(time.time())

            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)

    @classmethod
    def cancel_job(cls, args):
        logger.debug("cancel_job entry")
        import time
        id = args["id"]
        ret = JobMqOperations._cancel_job_op(args)
        if ret:
            logger.debug("cancel_job success")
            retdata = {}
            retdata["method"] = "cancel_job_resp"
            args_dict = {}
            args_dict["id"] = id
            args_dict["op_result"] = "success"
            args_dict["operatestatus"] = "cancelled"
            args_dict["jobstatus"] = "C"
            args_dict["endtime"] = int(time.time())
            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)
        else:
            logger.debug("cancel_job failed")
            retdata = {}
            retdata["method"] = "cancel_job_resp"
            args_dict = {}
            args_dict["id"] = id
            args_dict["op_result"] = "failed"
            args_dict["operatestatus"] = "cancelfailed"
            retdata["args"] = args_dict
            DBUtil().invoke_save(retdata)
        g_mq_create_job_event.set()

    @staticmethod
    def _parse_args_for_filejob(args):
        logger.debug("_parse_args_for_filejob entry")
        import os
        job = Job()
        job.id = args["id"]
        job.submiter = args["submiter"]
        job.jobname = args["jobname"]
        job.jobfilename = args["jobfilename"]
        job.workspace = args["workspace"]
        dir, filename = os.path.split(job.jobfilename)
        job.workingdir = dir
        return job

    @staticmethod
    def _parse_args_for_commonjob(args):
        logger.debug("_parse_args_for_commonjob %r entry" % args['type'])
        job = CommonJob()
        job.json_body = args["json_body"]
        job.type = args["type"]
        job.id = args["id"]
        job.submiter = args["submiter"]
        if "jobname" in args:
            job.jobname = args["jobname"]
        job.queue = args["queue"]
        job.walltime = args["walltime"]
        job.mail = args["mail"]
        job.mailtrigger = args["mailtrigger"]
        if "workingdir" in args:
            job.workingdir = args["workingdir"]
            if job.workingdir[-1] == '/' or job.workingdir[-1] == "\\":
                job.workingdir = job.workingdir[0:-1]
        job.workspace = args["workspace"]

        pnodescount = args["pnodescount"]
        ppn = args["ppn"]
        pmem = args["pmem"]
        if pnodescount > 0:
            job.nodescount = pnodescount
        if pnodescount > 0 and ppn > 0:
            job.cpuscount = pnodescount * ppn

        job.pnodescount = pnodescount
        job.ppn = ppn
        job.pmem = pmem
        return job

    @staticmethod
    def _submit_filejob(job):
        logger.debug("_submit_filejob entry")
        bcreate = True
        if job is None or not hasattr(job, 'jobfilename'):
            return False
        if job is None or not hasattr(job, 'workspace'):
            return False
        abs_job_file_path = JobUtil.get_real_path(job.jobfilename,
                                                  job.workspace)
        abs_working_dir = JobUtil.get_real_path(job.workingdir, job.workspace)
        submiter = job.submiter
        jobname = job.jobname

        jobid = JobManager().submit_job(abs_working_dir, abs_job_file_path,
                                        submiter, jobname)

        if jobid:
            job.jobid = jobid
            with g_jobop_lock:
                g_ui_jobs[jobid] = "Q"
        else:
            bcreate = False

        submit_ret = True
        if not bcreate:
            logger.error("_submit_filejob: can not get the jobid, "
                         "try to look for by name and submit_args")
            temp_jobid = JobMqOperations._look_for_jobid_by_name_and_args(
                jobname, abs_job_file_path)
            logger.info("Found jobid %s from name and args" % temp_jobid)
            if temp_jobid == '':
                raise Exception("_submit_filejob submit job failed "
                                "without jobid returned")
            jobid = temp_jobid
            job.jobid = jobid
            submit_ret = False

        jobinfo = JobManager().get_job(jobid)
        if not jobinfo:
            logger.error("_submit_filejob: get job info "
                         "failed when the created job")
            raise Exception("_submit_filejob get job info failed!")
        if hasattr(jobinfo, 'jobname') and jobinfo.jobname != "":
            job.jobname = jobinfo.jobname
        if hasattr(jobinfo, 'queue') and jobinfo.queue != "":
            job.queue = jobinfo.queue
        return submit_ret

    @staticmethod
    def _create_job_op(args):
        logger.debug("_create_job_op entry")
        type = args["type"]
        submit_ret = True
        try:
            if type == "file":
                logger.debug("_create_job_op file")
                job = JobMqOperations._parse_args_for_filejob(args)
                submit_ret = JobMqOperations._submit_filejob(job)
            else:
                logger.debug("_create_job_op %r" % type)
                job = JobMqOperations._parse_args_for_commonjob(args)
                JobManager().generate_commonjobfile(job)
                submit_ret = JobMqOperations._submit_filejob(job)
        except Exception:
            logger.error("_create_job_op failed with "
                         "exception" + traceback.format_exc())
            return False, None
        return submit_ret, job

    @staticmethod
    def _rerun_job_op(args):
        logger.debug("_rerun_job_op entry")
        try:
            job = Job()
            job.id = args["id"]
            job.workspace = args["workspace"]
            job.submiter = args["submiter"]
            job.jobfilename = args["jobfilename"]
            job.jobname = args["jobname"]
            job.workingdir = args["workingdir"]
            if job.jobfilename != "" and job.workingdir != "":
                JobMqOperations._submit_filejob(job)
            else:
                logger.error(
                    "_rerun_job_op Can not rerun the job : "
                    "since the jobfilename or workingdir parameter is empty!"
                )
                return False, None
        except Exception:
            logger.error("_rerun_job_op failed "
                         "with exception" + traceback.format_exc())
            return False, None
        return True, job

    @staticmethod
    def _cancel_job_op(args):
        logger.debug("canceljob entry")
        jobid = args["jobid"]
        user = args["user"]
        ret = JobManager().cancel_job(jobid, user)
        return ret

    @staticmethod
    def _look_for_jobid_by_name_and_args(job_name, job_submit_args):
        current_jobs = JobManager().get_alljob_status_info()
        find_jobid = ''
        for id in current_jobs:
            temp_job = JobManager().get_job(id, current_jobs[id])
            if temp_job is not None and temp_job.jobname == job_name \
                    and temp_job.submit_args == job_submit_args:
                find_jobid = temp_job.jobid
        return find_jobid
