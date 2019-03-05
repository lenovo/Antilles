# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from libs.components.scheduler.scheduler_torque import SchedulerTorque
from libs.components.scheduler.scheduler_lsf import SchedulerLSF
from libs.components.scheduler.scheduler_slurm import SchedulerSlurm
from libs.util.confutil import ConfUtil
import logging
import traceback
import sys

logger = logging.getLogger(__name__)
conf = ConfUtil.parse_paste_conf()


class JobManager(object):
    """
    classdocs
    """

    @property
    def scheduler(self):
        if conf['scheduler_software'] == "torque":
            return SchedulerTorque
        elif conf['scheduler_software'] == "lsf":
            return SchedulerLSF
        elif conf['scheduler_software'] == "slurm":
            return SchedulerSlurm
        else:
            return SchedulerTorque

    def get_job(self, jobid, job_status_info=None):
        return self.scheduler.get_job(jobid, job_status_info)

    def get_alljob_status_info(self):
        return self.scheduler.get_alljob_status_info()

    def submit_job(self, abs_working_dir, abs_jobfile_name, user, jobname=None):
        return self.scheduler.submit_job(abs_working_dir, abs_jobfile_name, user, jobname)

    def cancel_job(self, jobid, user):
        return self.scheduler.cancel_job(jobid, user)

    def get_allqueues(self, is_admin, usergroup):
        return self.scheduler.get_allqueues(is_admin, usergroup)

    def is_scheduler_working(self):
        return self.scheduler.is_scheduler_working()

    def generate_commonjobfile(self, commonjob):
        ret = True
        try:
            import subprocess
            import json
            import base64
            from libs.util.confutil import ConfUtil
            from libs.util.jobutil import JobUtil
            from time import localtime, strftime
            #check the workingdir to avoid injection
            import os
            check_workingdir = JobUtil.get_real_path(commonjob.workingdir, commonjob.workspace)
            if not os.path.isdir(check_workingdir):
                raise Exception("Invalid workingdir: " + commonjob.workingdir)
            logger.debug("generate_commonjobfile %r entry" % commonjob.type)
            jobfile_prefix = strftime("%Y%m%d%H%M", localtime())
            jobfilename = os.path.join(
                commonjob.workingdir, jobfile_prefix + '_' + commonjob.jobname + '_' + str(commonjob.id)
                                      + self.scheduler.get_jobfile_suffix()
            )
            absjobfilename = JobUtil.get_real_path(jobfilename, commonjob.workspace)
            job_gen_script = ConfUtil.get_jobgen_script(commonjob.type)
            """construct the command which using to generate job file"""
            command = [sys.executable, job_gen_script, '--output', absjobfilename, '--json',
                       base64.encodestring(commonjob.json_body), '--workspace', commonjob.workspace]
            logger.debug("generate_commonjobfile command %r" % ' '.join(command))
            #JobUtil.exec_oscmd(command)
            import subprocess
            subprocess.check_call(command)

            #modify the user and group of the job file which is generated
            if os.path.exists(absjobfilename):
                import pwd
                user = pwd.getpwnam(commonjob.submiter)
                os.chown(absjobfilename, user.pw_uid, user.pw_gid)
            else:
                ret = False
            commonjob.jobfilename = jobfilename
        except:
            logger.error("generate_commonjobfile failed " + traceback.format_exc())
            ret = False
        return ret
