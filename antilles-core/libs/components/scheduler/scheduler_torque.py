# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from libs.datamodule.jobdef import Job
from libs.util.jobutil import JobUtil
from libs.util.osutil import OSUtil
from libs.components.scheduler.scheduler_base import SchedulerBase
import re
import logging
import traceback
logger = logging.getLogger(__name__)


class SchedulerTorque(SchedulerBase):
    '''
    classdocs
    '''
    def __init__(self):
        pass;

    @staticmethod
    def convert_timestr_2_seconds(timestr):
        import time
        timeformat = "%a %b %d %H:%M:%S %Y"
        timestruct = time.strptime(timestr, timeformat)
        secs = time.mktime(timestruct)
        return int(secs)

    @staticmethod
    def get_alljob_status_info():
        alljob_status_info = {}
        try:
            rc,out,err = JobUtil.exec_oscmd("qstat -f")
            results = out.splitlines()
            if len(results) > 1:
                for line in results:
                    if 'Job Id: ' in line:
                        jobid = line.split('Job Id: ')[1].split('.')[0]
                        status = None
                        alljob_status_info[jobid] = {'info': [], 'status': None}
                    if 'job_state' in line:
                        status = line.split('=')[1].strip()
                    if status is not None and jobid is not None:
                        alljob_status_info[jobid]['status'] = status
                        status = None
                    if jobid in alljob_status_info:
                        alljob_status_info[jobid]['info'].append(line)
        except:
            logger.exception("get_alljob_status_info failed")
        return alljob_status_info

    #parse the output of scheduler command to return a job object
    #for torque, the command is "qstat -f jobid"
    @staticmethod
    def get_job(jobid, job_status_info=None):
        '''
        Job Id: 18.head
            Job_Name = ttt
            Job_Owner = hpcuser@localhost
            job_state = Q
            queue = batch
            server = head
            Checkpoint = u
            ctime = Fri Aug 17 02:46:28 2018
            Error_Path = head:/home/hpcuser/12306_test/ttt-84693.out
            Hold_Types = n
            Join_Path = oe
            Keep_Files = n
            Mail_Points = a
            mtime = Fri Aug 17 02:46:28 2018
            Output_Path = head:/home/hpcuser/12306_test/ttt-84693.out
            Priority = 0
            qtime = Fri Aug 17 02:46:28 2018
            Rerunable = True
            Resource_List.neednodes = 1:ppn=1
            Resource_List.nodect = 1
            Resource_List.nodes = 1:ppn=1
            substate = 10
            Variable_List = PBS_O_QUEUE=batch,PBS_O_HOME=/home/hpcuser,
            PBS_O_LOGNAME=hpcuser,
            PBS_O_PATH=/usr/local/cuda/bin:/opt/xcat/bin:/opt/xcat/sbin:/opt/xcat
            /share/xcat/tools:/opt/ohpc/pub/libs/singularity/2.4/bin:/opt/ohpc/pub
            /mpi/openmpi3-gnu7/3.0.0/bin:/opt/ohpc/pub/compiler/gcc/7.2.0/bin:/opt
            /ohpc/pub/utils/prun/1.2:/opt/ohpc/pub/bin:/usr/local/cuda/bin:/opt/co
            nfluent/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/ho
            me/hpcuser/.local/bin:/home/hpcuser/bin,
            PBS_O_MAIL=/var/spool/mail/hpcuser,PBS_O_SHELL=/bin/bash,
            PBS_O_LANG=en_US.UTF-8,PBS_O_INITDIR=/home/hpcuser/12306_test,
            PBS_O_WORKDIR=/home/hpcuser/12306_test,PBS_O_HOST=head,
            PBS_O_SERVER=head
            euser = hpcuser
            egroup = pretrain_demo
            queue_rank = 4
            queue_type = E
            etime = Fri Aug 17 02:46:28 2018
            submit_args = -N ttt /home/hpcuser/12306_test/201808170246_ttt_84693.pbs
            fault_tolerant = False
            job_radix = 0
            submit_host = head
        '''
        job = Job()
        job.jobid = jobid
        try:
            import re
            import json
            import time

            if job_status_info is None:
                cmd = "qstat -f " + job.jobid
                rc,out,err = JobUtil.exec_oscmd(cmd)
                job_info = out.splitlines()
                if len(job_info) > 0:
                    del job_info[0]
                else:
                    logger.exception("Get job {0} detail info failed: {1}".format(job.jobid, err))
                    return None
            else:
                job_info = job_status_info['info']

            #pre format the queue string
            job_lines = []
            job_last_line = ""
            curtime = int(time.time())
            for line in job_info:
                regx = re.compile(r'^\s{4}\w+')
                if regx.match(line):
                    if len(job_last_line) > 0: job_lines.append(job_last_line)
                    job_last_line = line.strip()
                else:
                    job_last_line = job_last_line + line.strip()
            if len(job_last_line) > 0:
                job_lines.append(job_last_line)

            jobproperties = {}
            for job_line in job_lines:
                job_line = job_line.strip()
                items = job_line.split("=", 1)
                if len(items) == 2:
                    key = items[0].strip()
                    value = items[1].strip()
                    jobproperties[key] = value
            server = None
            for (key,value) in jobproperties.items():
                key = key.lower()
                value = value.strip()
                if key == "job_name":
                    job.jobname = value
                elif key == "job_owner":
                    job.submiter = value.split("@")[0]
                elif key == "job_state":
                    if job_status_info is None:
                        job.jobstatus = value
                    else:
                        job.jobstatus = job_status_info['status']
                elif key == "queue":
                    job.queue = value
                elif key == 'server':
                    server = value
                elif key == "error_path":
                    job.errfile = value
                elif key == "output_path":
                    job.outfile = value
                elif key == "exec_host":
                    totalcpucounts = 0
                    hosts_nodes = {}
                    try:
                        hostlist = value.split('+')
                        for hostone in hostlist:
                            items = hostone.split('/')
                            onenodecpucount = 0
                            cpugroups = items[1].split(",")
                            for cpugroup in cpugroups:
                                cpus = cpugroup.split("-")
                                if len(cpus) == 1:
                                    onenodecpucount += 1
                                else:
                                    onenodecpucount += (int(cpus[1]) - int(cpus[0]) + 1)
                            totalcpucounts = totalcpucounts + onenodecpucount
                            hosts_nodes[items[0]] = onenodecpucount
                    except:
                        logger.error("getjob parse cpucount failed"+ traceback.format_exc())

                    job.cpuscount = totalcpucounts
                    job.hosts_cpus = json.dumps(hosts_nodes)
                elif key == "submit_args":
                    job.submit_args = value.split()[-1]
                elif key == "priority":
                    job.priority = value
                elif key == "qtime":
                    job.qtime = SchedulerTorque.convert_timestr_2_seconds(value)
                elif key == "resource_list.nodect":
                    job.nodescount = int(value)
                elif key == "resource_list.walltime":
                    job.walltime = value
                elif key == "start_time":
                    job.starttime = SchedulerTorque.convert_timestr_2_seconds(value)
                elif key == "comp_time":
                    job.endtime = SchedulerTorque.convert_timestr_2_seconds(value)
                    if job.endtime > curtime:
                        job.endtime = curtime

            if job.jobstatus.lower() == "q":
                job.starttime = 0
            elif job.jobstatus.lower() == "r":
                job.endtime = 0
            if server is not None and job.errfile.startswith(server + ':'):
                job.errfile = job.errfile.lstrip(server + ':')
                job.outfile = job.outfile.lstrip(server + ':')
            return job
        except:
            logger.error("getjob failed"+ traceback.format_exc())
            return None

    #using linux account 'user' to cancel one job
    #for torque, the command is "canceljob jobid"
    @staticmethod
    def cancel_job(jobid, user):
        try:
            logger.debug("canceljob entry")
            cmd = "canceljob " + jobid
            rc,out,err = JobUtil.exec_oscmd_with_user(user, cmd)
            if out.find("cancelled") != -1 or out.find("cancelling") != -1:
                return True
            else:
                logger.error("canceljob failed: canceljob command ret=" + err)
                return False
        except:
            logger.error("canceljob failed: except")
            return False

    #submit one job through jobfile
    #for torque the command is "qsub jobfile"
    @staticmethod
    def submit_job(abs_working_dir, abs_jobfile_name, user, jobname=None):
        try:
            logger.debug("subjob entry")
            import os, re
            if not os.path.isdir(abs_working_dir):
                logger.error("submit_job failed: Invalid working directory: " + abs_working_dir)
                return None
            if jobname:
                cmd = "qsub -N '" + jobname + "' '" + abs_jobfile_name + "'"
            else:
                cmd = "qsub '" + abs_jobfile_name + "'"
            rc,out,err = JobUtil.exec_oscmd_with_user_underdir(user, cmd, abs_working_dir)
            reg = re.compile(r'^(\d+)(.)(.+)')
            ret = reg.findall(out)
            if len(ret) == 1:
                jobid = ret[0][0]
                return jobid
            else:
                logger.debug("submit_job failed: no job id is returned command, command ret =" + err)
                return None
        except:
            logger.error("subjob failed: except")
            return None

    @staticmethod
    def get_allqueues(is_admin=False, usergroup=None):
        queues_list = []
        try:
            logger.debug("get_allqueues entry")
            rc,out,err = JobUtil.exec_oscmd("qstat -Q")
            lines = out.splitlines()
            linecount = len(lines)
            if linecount <= 2:
                return queues_list

            for i in range(2,linecount):
                data = {}
                line = lines[i]
                items = line.split()
                if len(items) > 5 and items[3].strip() == "yes" and items[4].strip() == "yes":
                    data['name'] = items[0].strip()
                    data['cores'] = None
                    data['nodes'] = None
                    data['run_time'] = None
                    data['state'] = None
                    data['max_nodes'] = None
                    data['max_cores_per_node'] = None
                    data['def_mem_per_node'] = None
                    data['max_mem_per_node'] = None
                    queues_list.append(data)
            return queues_list
        except:
            logger.error("get_allqueues failed: except")
            return queues_list

    @staticmethod
    def is_scheduler_working():
        scheduler_chk_cmds = [
            ['service', 'trqauthd', 'status'],
            ['service', 'pbs_server', 'status'],
            ['service', 'maui.d', 'status']
        ]
        for chk_cmd in scheduler_chk_cmds:
            rc, out, err = OSUtil.safe_popen(chk_cmd)
            lines = out.splitlines()
            linecount = len(lines)
            if linecount < 1:
                return False
            if linecount < 2:
                if not re.search(r'is running...', out):
                    return False
            else:
                for line in lines:
                    if re.search(r'Active: active \(running\)', line):
                        break
                    if not line:
                        return False
        return True

    @staticmethod
    def get_jobfile_suffix():
        return ".pbs"
