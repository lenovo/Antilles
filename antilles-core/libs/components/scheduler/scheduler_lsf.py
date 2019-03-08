# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
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


class SchedulerLSF(SchedulerBase):
    '''
    classdocs
    '''
    def __init__(self):
        pass

    @staticmethod
    def convert_hosts(hosts_str, average_gpu_num):
        rethosts = {}
        hosts = hosts_str.strip()[1:-1].split('> <')
        for host in hosts:
            items = host.split('*')
            if len(items) == 2:
                rethosts[items[1]] = items[0]
            else:
                if rethosts.has_key(items[0]):
                    rethosts[items[0]] = rethosts[items[0]] + 1
                else:
                    rethosts[items[0]] = 1
        retgpuhosts = {nodename: average_gpu_num for nodename in rethosts.keys()}

        return rethosts, retgpuhosts

    @staticmethod
    def convert_job_status(lsfstatus):
        if lsfstatus == "PEND" or lsfstatus == "PROV" or lsfstatus == 'FWD_PEND':
            return "Q"
        elif lsfstatus == "RUN":
            return "R"
        elif lsfstatus == "PSUSP" or lsfstatus == "SSUSP" or lsfstatus == "USUSP" or lsfstatus == "SUSP":
            return "S"
        elif lsfstatus == "DONE" or lsfstatus == "EXIT":
            return "C"
        elif lsfstatus == "WAIT":
            return "W"
        else:
            return "H"

    @staticmethod
    def convert_timestr_2_seconds(timestr):
        import time
        year = time.localtime().tm_year
        timestr = timestr + " " + str(year)
        timeformat = "%a %b %d %H:%M:%S %Y"
        timestruct = time.strptime(timestr, timeformat)
        secs = time.mktime(timestruct)
        return int(secs)

    @staticmethod
    def get_alljob_status_info():
        alljob_status_info = {}
        try:
            rc,out,err = JobUtil.exec_oscmd("bjobs -UF -a -l -u all")
            out = out.replace('\n                     ', '')
            lines = [s for s in out.splitlines() if s.strip() != '']
            if len(lines) > 1 and lines[0].find("Job") == 0:
                for line in lines:
                    if 'Job' in line:
                        items = line.split(',')
                        for item in items:
                            if 'Job <' in item:
                                jobid = item.split('<')[1].split('>')[0]
                                status = None
                                alljob_status_info[jobid] = {'info': [], 'status': None}
                            if 'Status <' in item:
                                status = item.split('<')[1].split('>')[0]
                                status = SchedulerLSF.convert_job_status(status)
                            if status is not None and jobid is not None:
                                alljob_status_info[jobid]['status'] = status
                                status = None
                    if jobid in alljob_status_info:
                        alljob_status_info[jobid]['info'].append(line)
        except:
            logger.error("get_alljob_status_info failed"+ traceback.format_exc())
        return alljob_status_info

    #parse the output of scheduler command to return a job object
    #for torque, the command is "bjobs -UF jobid"
    @staticmethod
    def get_job(jobid, job_status_info=None):
        '''
        Job <141>, Job Name <ddd>, User <hpcuser>, Project <default>, Status <RUN>, Que
                            ue <short>, Command <#!/bin/bash;#BSUB -J ls_113;#BSUB -o 
                            ls_113-84665.out;#BSUB -e ls_113-84665.out;#BSUB -q short;
                            #BSUB -cwd /home/hpcuser/12306_test;#BSUB -n 1;#BSUB -R sp
                            an[ptile=1];echo job start time is `date` ;echo `hostname`
                            ;cd /home/hpcuser/12306_test;sleep 100;echo job end time 
                            is `date` >, Share group charged </hpcuser>, Job Descripti
                            on <201808161049_ls_113_84665.lsf>
        Thu Aug 16 23:39:20: Submitted from host <head>, CWD <$HOME/12306_test>, Specif
                            ied CWD <$HOME/12306_test>, Output File <ls_113-84665.out>
                            , Requested Resources <span[ptile=1]>;
        Thu Aug 16 23:39:21: Started 1 Task(s) on Host(s) <head>, Allocated 1 Slot(s) o
                            n Host(s) <head>, Execution Home </home/hpcuser>, Executio
                            n CWD </home/hpcuser/12306_test>;

        SCHEDULING PARAMETERS:
                r15s   r1m  r15m   ut      pg    io   ls    it    tmp    swp    mem
        loadSched   -    0.9    -     -       -     -    -     -     -      -      -  
        loadStop    -     -     -     -       -     -    -     -     -      -      -  

        RESOURCE REQUIREMENT DETAILS:
        Combined: select[type == local] order[r15s:pg] span[ptile=1]
        Effective: select[type == local] order[r15s:pg] span[ptile=1] 
        '''
        job = Job()
        job.jobid = jobid
        try:
            import re
            import json
            import time
            from os import path, sep

            if job_status_info is None:
                cmd = "bjobs -UF " + job.jobid
                rc,out,err = JobUtil.exec_oscmd(cmd)
                job_info = [s for s in out.splitlines() if s.strip() != '']
                if len(job_info) <= 0:
                    logger.exception("Get job {0} detail info failed: {1}".format(job.jobid, err))
                    return None
            else:
                job_info = job_status_info['info']

            sub_pattern = re.compile(r'^(.*): Submitted from.*')
            start_pattern = re.compile(
                r'^(.*): Started (\d+) Task\(s\) on Host\(s\)(.*), Allocated.*')
            comp_pattern = re.compile(r'^(.*; )?(.*): Completed.*')
            done_pattern = re.compile(r'^(.*): Done successfully.*')
            walltime_pattern = re.compile(r'^(.*)RUNLIMIT.*')
            gpu_pattern = re.compile(r'^(.*)\[ngpus=(\d+).*')

            numgpus_per_node = 0
            hosts_str = ""
            curtime = int(time.time())
            workdir = None
            for i in range(len(job_info)):
                if job_info[i].startswith("Job <"):
                    items = job_info[i].split('>,')
                    if items[-1].endswith('>'):
                        items[-1] = items[-1][:-1]
                    for item in items:
                        KVs = item.split('<')
                        if len(KVs) == 2:
                            key = KVs[0].strip()
                            value = KVs[1].strip()
                            if key == 'Job Name':
                                job.jobname = value
                            elif key == 'Status':
                                if job_status_info is None:
                                    job.jobstatus = SchedulerLSF.convert_job_status(
                                        value)
                                else:
                                    job.jobstatus = job_status_info['status']
                            elif key == 'Queue':
                                job.queue = value
                            elif key == 'User':
                                job.submiter = value
                            elif key == 'Command':
                                job.submit_args = value[:250]
                elif sub_pattern.match(job_info[i]):
                    items = re.split('>[,|;]', job_info[i])
                    job.qtime = SchedulerLSF.convert_timestr_2_seconds(
                        sub_pattern.search(items[0]).groups()[0])
                    for item in items:
                        KVs = item.split('<')
                        if len(KVs) == 2:
                            key = KVs[0].strip()
                            value = KVs[1].strip()
                            if key == 'Output File':
                                job.outfile = repr(value).strip('\'')
                            elif key == 'Error File':
                                job.errfile = repr(value).strip('\'')
                elif start_pattern.match(job_info[i]):
                    job.starttime = SchedulerLSF.convert_timestr_2_seconds(
                        start_pattern.search(job_info[i]).groups()[0])
                    job.cpuscount = int(
                        start_pattern.search(job_info[i]).groups()[1])
                    hosts_str = start_pattern.search(job_info[i]).groups()[2]
                    workdir = job_info[i].split()[-1]
                    workdir = workdir[1:-2]
                elif gpu_pattern.match(job_info[i]):
                    numgpus_per_node = int(
                        gpu_pattern.search(job_info[i]).groups()[1])
                elif comp_pattern.match(job_info[i]):
                    job.endtime = SchedulerLSF.convert_timestr_2_seconds(
                        comp_pattern.search(job_info[i]).groups()[1])
                elif done_pattern.match(job_info[i]):
                    job.endtime = SchedulerLSF.convert_timestr_2_seconds(
                        done_pattern.search(job_info[i]).groups()[0])
                    if job.endtime > curtime:
                        job.endtime = curtime
                elif walltime_pattern.match(job_info[i]):
                    job.walltime = job_info[i + 1].split('of')[0].strip()
            if job.outfile and not job.outfile.startswith(sep) and workdir:
                job.outfile = path.join(workdir, job.outfile)
            if job.errfile and not job.errfile.startswith(sep) and workdir:
                job.errfile = path.join(workdir, job.errfile)
            if hosts_str:
                hosts_nodes, gpu_hosts_nodes = SchedulerLSF.convert_hosts(
                    hosts_str, numgpus_per_node)
                job.hosts_cpus = json.dumps(hosts_nodes)
                job.nodescount = len(hosts_nodes.keys())
                if numgpus_per_node:
                    job.gpuscount = job.nodescount * numgpus_per_node
                    job.hosts_gpus = json.dumps(gpu_hosts_nodes)
            if job.jobstatus.lower() == "q":
                job.starttime = 0
            elif job.jobstatus.lower() == "r":
                job.endtime = 0
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
            cmd = "bkill " + jobid
            rc,out,err = JobUtil.exec_oscmd_with_user(user, cmd)
            if out.find("being terminated") != -1:
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
                cmd = "bsub -J '" + jobname + "' -Jd '"+ abs_jobfile_name + "' < '" + abs_jobfile_name + "'"
            else:
                cmd = "bsub -Jd '" + abs_jobfile_name + "' < '" + abs_jobfile_name + "'"
            rc,out,err = JobUtil.exec_oscmd_with_user_underdir(user, cmd, abs_working_dir)
            reg = re.compile(r'^Job <(\d+)>')
            ret = reg.findall(out)
            if len(ret) == 1:
                jobid = ret[0]
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
            rc,out,err = JobUtil.exec_oscmd("bqueues")
            lines = out.splitlines()
            linecount = len(lines)
            if linecount <= 1:
                return queues_list

            for i in range(1,linecount):
                data = {}
                line = lines[i]
                items = line.split()
                if len(items) > 3 and items[2].strip() == "Open:Active":
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
            'badmin', 'showstatus'
        ]
        rc, out, err = OSUtil.safe_popen(scheduler_chk_cmds, timeout=3, interval=1)

        if not re.search(r'LSF is down', err):
            return True

        return False

    @staticmethod
    def get_jobfile_suffix():
        return ".lsf"


if __name__ == '__main__':
    s = '<slave> <slave> <master> <master>'
    print SchedulerLSF.convert_hosts(s, 1)

