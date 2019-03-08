# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from libs.datamodule.jobdef import Job
from libs.util.jobutil import JobUtil
from libs.components.scheduler.scheduler_base import SchedulerBase
from antilles.scheduler.exceptions import QueueExistException,\
    NodeNotExistException
import re
import logging
import traceback
import os
import pwd
from django.conf import settings

logger = logging.getLogger(__name__)


class SchedulerSlurm(SchedulerBase):
    '''
    classdocs
    '''

    def __init__(self):
        pass

    @staticmethod
    def convert_hosts(hosts_str, average_cpu_num, average_gpu_num):
        import re

        hosts = []
        noderange_pattern = re.compile(r'([^,\[]*)(\[[^\]]*\])?(.*)')

        items = hosts_str.split(',')
        for item in items:
            item = item.strip()
            if noderange_pattern.match(item):
                prefix, rangelist, rest = \
                    noderange_pattern.search(item).groups()

                if not rangelist:
                    hosts.extend([prefix])
                else:
                    m = re.match(r'^([0-9]+)-([0-9]+)$', rangelist[1:-1])

                    (s_low, s_high) = m.group(1, 2)
                    low = int(s_low)
                    high = int(s_high)
                    width = len(s_low)

                    results = []
                    for i in xrange(low, high + 1):
                        results.append("%s%0*d" % (prefix, width, i))
                    hosts.extend(results)

        rethosts = {nodename: average_cpu_num for nodename in hosts}
        retgpuhosts = {nodename: average_gpu_num for nodename in hosts}

        return rethosts, retgpuhosts

    @staticmethod
    def convert_job_status(slurmstatus):
        if slurmstatus in ("PENDING", "CONFIGURING", "SPECIAL_EXIT"):
            return "Q"
        elif slurmstatus in ("COMPLETED", "FAILED", "NODE_FAIL", "BOOT_FAIL",
                             "TIMEOUT", "COMPLETING"):  # COMPLETED
            return "C"
        elif slurmstatus == "RUNNING":
            return "R"
        elif slurmstatus == "SUSPENDED":
            return "S"
        elif slurmstatus == "CANCELLED":
            return "cancelled"
        else:
            return "H"

    @staticmethod
    def convert_timestr_2_seconds(timestr):
        try:
            import time
            timeformat = "%Y-%m-%dT%H:%M:%S"
            timestruct = time.strptime(timestr, timeformat)
            secs = time.mktime(timestruct)
            return int(secs)
        except BaseException:
            return 0

    @staticmethod
    def convert_gpu_num(gres):
        for item in gres.split(','):
            gres_item = item.split(':')
            if gres_item[0] == 'gpu':
                return int(gres_item[1])

    @staticmethod
    def get_alljob_status_info():
        alljob_status_info = {}
        try:
            rc, out, err = JobUtil.exec_oscmd("scontrol show jobs")
            lines = out.splitlines()
            index = 0
            status = None
            jobid = None
            for line in lines:
                if line.find("JobId") == 0:
                    jobid = line.split()[0].split("=")[1].strip()
                    status = None
                    alljob_status_info[jobid] = {'info': [], 'status': None}
                if line.strip().find("JobState") == 0:
                    status = line.split()[0].split("=")[1]
                    status = SchedulerSlurm.convert_job_status(status)
                if status is not None and jobid is not None:
                    alljob_status_info[jobid]['status'] = status
                    status = None
                if jobid in alljob_status_info:
                    alljob_status_info[jobid]['info'].append(line)

        except BaseException:
            logger.error("get_alljob_status_info failed" + traceback.format_exc())
        return alljob_status_info

    # parse the output of scheduler command to return a job object
    # for torque, the command is "qstat -f jobid"
    @staticmethod
    def get_job(jobid, job_status_info=None):
        '''
        JobId=61311 JobName=single
           UserId=root(0) GroupId=root(0) MCS_label=N/A
           Priority=4294901630 Nice=0 Account=(null) QOS=(null)
           JobState=COMPLETED Reason=None Dependency=(null)
           Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
           RunTime=00:00:14 TimeLimit=UNLIMITED TimeMin=N/A
           SubmitTime=2018-08-17T10:51:39 EligibleTime=2018-08-17T10:51:39
           StartTime=2018-08-17T10:51:40 EndTime=2018-08-17T10:51:54 Deadline=N/A
           PreemptTime=None SuspendTime=None SecsPreSuspend=0
           Partition=compute AllocNode:Sid=head:326299
           ReqNodeList=(null) ExcNodeList=(null)
           NodeList=head
           BatchHost=head
           NumNodes=1 NumCPUs=28 NumTasks=0 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
           TRES=cpu=28,node=1
           Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
           MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
           Features=(null) DelayBoot=00:00:00
           Gres=gpu:1 Reservation=(null)
           OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
           Command=/home/hpcadmin/ai_cmd/single_20180817105139.slurm
           WorkDir=/home/hpcadmin/ai_cmd/
           StdErr=/home/hpcadmin/ai_cmd//slurm-61311.out
           StdIn=/dev/null
           StdOut=/home/hpcadmin/ai_cmd//slurm-61311.out
           Power=
        '''
        job = Job()
        job.jobid = jobid
        try:
            import re
            import json
            import time

            if job_status_info is None:
                cmd = "scontrol show jobs " + job.jobid

                # in case of slurm_load_jobs error occurred, retry
                retry_time = 3
                for _ in range(retry_time):
                    rc, out, err = JobUtil.exec_oscmd(cmd)
                    job_info = [s for s in out.splitlines() if s.strip() != '']
                    if len(job_info) > 0:
                        break
                    time.sleep(0.4)
                else:
                    logger.exception(
                        "Get job {0} detail info failed: {1}".format(
                            job.jobid, err))
                    return None
            else:
                job_info = job_status_info['info']

            nodelists = ""
            numtasks = 0
            numcpus_per_task = 0
            numgpus_per_node = 0
            min_cpus_node = 0
            curtime = int(time.time())
            for line in job_info:
                items = line.split()
                for item in items:
                    params = item.split("=")
                    key = params[0].strip()
                    value = params[1].strip()

                    if key == "JobName":
                        job.jobname = value
                    elif key == 'JobState':
                        if job_status_info is None:
                            job.jobstatus = SchedulerSlurm.convert_job_status(
                                value)
                        else:
                            job.jobstatus = job_status_info['status']
                    elif key == 'Command':
                        job.submit_args = value[:250]
                    elif key == 'SubmitTime':
                        job.qtime = SchedulerSlurm.convert_timestr_2_seconds(
                            value)
                    elif key == 'StartTime':
                        job.starttime = \
                            SchedulerSlurm.convert_timestr_2_seconds(value)
                    elif key == 'EndTime':
                        job.endtime = SchedulerSlurm.convert_timestr_2_seconds(
                            value)
                        if job.endtime > curtime:
                            job.endtime = curtime
                    elif key == 'Partition':
                        job.queue = value
                    elif key == 'StdOut':
                        job.outfile = value
                    elif key == 'StdErr':
                        job.errfile = value
                    elif key == 'TimeLimit':
                        job.walltime = value
                    elif key == 'NodeList':
                        nodelists = value
                    elif key == 'NumNodes':
                        job.nodescount = int(
                            value) if job.jobstatus in ('R', 'C') else 0
                    elif key == 'NumCPUs':
                        job.cpuscount = int(value)
                    elif key == 'NumTasks':
                        numtasks = int(value)
                    elif key == 'CPUs/Task':
                        numcpus_per_task = int(value)
                    elif key == 'UserId':
                        job.submiter = value.split("(")[0]
                    elif key == 'WorkDir':
                        job.workingdir = value
                    elif key == 'Gres':
                        numgpus_per_node = \
                            SchedulerSlurm.convert_gpu_num(value)
                    elif key == 'MinCPUsNode':
                        min_cpus_node = int(value)
            if nodelists and numcpus_per_task and job.nodescount:
                average_cpu_num = max(job.cpuscount, numtasks *
                                      numcpus_per_task) / job.nodescount
                average_cpu_num = min_cpus_node\
                    if not average_cpu_num else average_cpu_num
                hosts_nodes, gpu_hosts_nodes = SchedulerSlurm.convert_hosts(
                    nodelists, average_cpu_num, numgpus_per_node)
                if average_cpu_num:
                    job.hosts_cpus = json.dumps(hosts_nodes)

                if numgpus_per_node:
                    job.gpuscount = len(hosts_nodes.keys()) * numgpus_per_node
                    job.hosts_gpus = json.dumps(gpu_hosts_nodes)

            if job.jobstatus.lower() == "q":
                job.starttime = 0
            elif job.jobstatus.lower() == "r":
                job.endtime = 0
            return job
        except BaseException:
            logger.error("getjob failed" + traceback.format_exc())
            return None

    # using linux account 'user' to cancel one job
    # for torque, the command is "canceljob jobid"
    @staticmethod
    def cancel_job(jobid, user):
        try:
            logger.debug("canceljob entry")
            cmd = "scancel " + jobid
            rc, out, err = JobUtil.exec_oscmd_with_user(user, cmd)
            if rc == 0:
                return True
            else:
                logger.error("canceljob failed: canceljob command ret=" + err)
                return False
        except BaseException:
            logger.error("canceljob failed: except")
            return False

    # submit one job through jobfile
    # for torque the command is "qsub jobfile"
    @staticmethod
    def submit_job(abs_working_dir, abs_jobfile_name, user, jobname=None):
        try:
            logger.debug("subjob entry")
            import os
            if not os.path.isdir(abs_working_dir):
                logger.error("submit_job failed: Invalid working directory: "
                             + abs_working_dir)
                return None
            import re
            if jobname:
                cmd = "sbatch -J " + jobname + " '" + abs_jobfile_name + "'"
            else:
                cmd = "sbatch '" + abs_jobfile_name + "'"
            rc, out, err = JobUtil.exec_oscmd_with_user_underdir(
                user, cmd, abs_working_dir)

            reg = re.compile(r'.*job (\d+)')
            ret = reg.findall(out)
            if len(ret) == 1:
                jobid = ret[0]
                return jobid
            else:
                logger.debug("submit_job failed: no job id is returned "
                             "command, command ret =" + err)
                return None
        except BaseException:
            logger.error("subjob failed: except")
            return None

    @staticmethod
    def get_allqueues(is_admin=False, usergroup=None):
        queues_list = []
        import subprocess
        try:
            logger.debug("get_allqueues entry")
            rc, out, err = JobUtil.exec_oscmd("sinfo")
            lines = out.splitlines()
            linecount = len(lines)
            queues_name = []
            if linecount <= 1:
                return queues_list

            for i in range(1, linecount):
                line = lines[i]
                items = line.split()
                data = {}
                name = items[0]
                check_queue = subprocess.check_output(
                    ['sinfo', '-p', name],
                    preexec_fn=SchedulerSlurm._set_gid_uid)
                if len(check_queue.split('\n')[1]) == 0:
                    name = name[:-1]
                if name in queues_name:
                    continue
                queues_name.append(name)
                if name != "":
                    queues = subprocess.check_output(
                        ['scontrol', 'show', 'partition', '-o', name],
                        preexec_fn=SchedulerSlurm._set_gid_uid)
                    queues = dict(
                        map(lambda x: (x.split('=')[0].upper(),
                                       x.split('=')[1]), queues.split()))
                    allow_groups = queues['ALLOWGROUPS'].strip().split(',')
                    if not is_admin and 'ALL' not in allow_groups \
                            and usergroup not in allow_groups:
                        continue
                    data['name'] = name
                    data['cores'] = queues['TOTALCPUS']
                    data['nodes'] = queues['TOTALNODES']
                    data['run_time'] = queues['MAXTIME']
                    data['state'] = queues['STATE']
                    data['max_nodes'] = queues['MAXNODES']
                    data['max_cores_per_node'] = queues['MAXCPUSPERNODE']
                    data['def_mem_per_node'] = queues['DEFMEMPERNODE']
                    data['max_mem_per_node'] = queues['MAXMEMPERNODE']
                    queues_list.append(data)
            return list(queues_list)
        except BaseException:
            logger.error("get_allqueues failed: except")
            return queues_list

    @staticmethod
    def is_scheduler_working():
        try:
            rc, out, err = JobUtil.exec_oscmd("scontrol ping")
            lines = out.splitlines()
            linecount = len(lines)
            if linecount < 1:
                return False

            for i in range(linecount):
                line = lines[i]
                items = line.split()
                if len(items) < 1 or items[0] != "Slurmctld(primary/backup)":
                    continue

                if not re.search(r'UP', items[len(items) - 1]):
                    return False
                else:
                    return True
        except BaseException:
            logger.error("scheduler is not working: except")
            return False

    @staticmethod
    def get_jobfile_suffix():
        return ".slurm"

    @staticmethod
    def get_queues_info():
        import subprocess
        columns_mapping = {
            'PARTITION': 'queue_name',
            'AVAIL': 'avail',
            'TIMELIMIT': 'timelimit',
            'NODES': 'nodes',
            'STATE': 'state',
            'NODELIST': 'node_list'
        }
        try:
            data = {}
            queue = subprocess.check_output(
                ['sinfo'], preexec_fn=SchedulerSlurm._set_gid_uid)[:-1]
            title = queue.split('\n')[0].split()
            for q in queue.split('\n')[1:]:
                query, datas = {}, {}
                if q[0] == ' ':
                    continue
                else:
                    q = q.split()
                for i in range(len(title)):
                    query[columns_mapping[title[i]]] = \
                        q[title.index(title[i])] if len(q) > i else ""
                queue_name = query['queue_name']
                check_queue = subprocess.check_output(
                    ['sinfo', '-p', queue_name],
                    preexec_fn=SchedulerSlurm._set_gid_uid)
                if len(check_queue.split('\n')[1]) == 0:
                    queue_name = queue_name[:-1]
                node_state = query['state']
                if queue_name not in data:
                    queues = subprocess.check_output(
                        ['scontrol', 'show', 'partition', '-o', queue_name],
                        preexec_fn=SchedulerSlurm._set_gid_uid)
                    queues = dict(
                        map(lambda x: (x.split('=')[0].upper(),
                                       x.split('=')[1]), queues.split()))
                    datas['queue_name'] = queue_name
                    datas['avail'] = query['avail'].upper()
                    datas['priority'] = int(queues['PRIORITYTIER'])
                    datas['default'] = True \
                        if queues['DEFAULT'] == 'YES' else False
                    datas['user_groups'] = [queues['ALLOWGROUPS']]
                    datas['nodes_total'] = {node_state: query['nodes']}
                    datas['nodes_list'] = {node_state: query['node_list']}
                    data[queue_name] = datas
                else:
                    data[queue_name]['nodes_total'][node_state] = \
                        query['nodes']
                    data[queue_name]['nodes_list'][node_state] = \
                        query['node_list']
        except BaseException:
            logger.exception("Get Queues Info Message Error")
            return None
        return data.values()

    @staticmethod
    def create_queues_info(data):
        import subprocess
        queue_name = data['queue_name']
        node_list = data['node_list']
        default = data['default']
        priority = data['priority']
        max_time = data['max_time']
        over_subscribe = data['over_subscribe']
        user_groups = data['user_groups']
        avail = data['avail']

        node_list = node_list.replace(' ', ',')
        try:
            queue = subprocess.check_output(
                ['sinfo', '-p', queue_name],
                preexec_fn=SchedulerSlurm._set_gid_uid)
        except BaseException:
            logger.exception("Create Queues Error")
            return None
        if len(queue.split('\n')[1]) > 0:
            logger.exception("Queues Name Already Exist.")
            raise QueueExistException
        try:
            subprocess.check_call(['scontrol', 'show', 'Node', node_list],
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
        except BaseException:
            logger.exception("Node Name Not Exist.")
            raise NodeNotExistException
        try:
            default = 'YES' if default else 'NO'
            parameter = 'PartitionName={} Nodes={} Default={} Priority={} ' \
                        'MaxTime={} OverSubscribe={} AllowGroups={} State={}'\
                .format(queue_name, node_list, default, priority, max_time,
                        over_subscribe, ','.join(user_groups), avail).split()
            subprocess.check_call(['scontrol', 'create'] + parameter,
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
            SchedulerSlurm._save_slurm_conf()
        except BaseException:
            logger.exception("Create Queues Error")
            return None
        return True

    @staticmethod
    def update_node_state(node_list, action, username):
        import subprocess
        columns_mapping = {
            'resume': 'resume',
            'down': 'down'
        }
        try:
            nodename = "Nodename={}".format(node_list.replace(' ', ','))
            if action in columns_mapping:
                action = columns_mapping[action]
            else:
                logger.error("Key Error! The Key Not In Columns_Mapping")
                return False
            state = "State={}".format(action)
            list_cmd = ["scontrol", "update", nodename, state]
            if action == 'down':
                list_cmd.append("Reason=down by {}".format(username))
            subprocess.check_call(list_cmd,
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
        except BaseException:
            logger.exception("Update Queues Nodes State Failed")
            return False
        return True

    @staticmethod
    def get_queues_detail(queue_name):
        import subprocess
        columns_mapping = {
            'PARTITION': 'queue_name',
            'AVAIL': 'avail',
            'TIMELIMIT': 'timelimit',
            'NODES': 'nodes',
            'STATE': 'state',
            'NODELIST': 'node_list'
        }
        try:
            data = {}
            queue = subprocess.check_output(
                ['sinfo', '--partition', queue_name],
                preexec_fn=SchedulerSlurm._set_gid_uid)[:-1]
            title = queue.split('\n')[0].split()
            for q in queue.split('\n')[1:]:
                query, datas = {}, {}
                q = q.split()
                for i in range(len(title)):
                    query[columns_mapping[title[i]]] = \
                        q[title.index(title[i])] if len(q) > i else ""
                node_state = query['state']
                if queue_name not in data:
                    queues = subprocess.check_output(
                        ['scontrol', 'show', 'partition', '-o', queue_name],
                        preexec_fn=SchedulerSlurm._set_gid_uid)
                    queues = dict(
                        map(lambda x: (x.split('=')[0].upper(),
                                       x.split('=')[1]), queues.split()))
                    datas['queue_name'] = queue_name
                    datas['avail'] = query['avail'].upper()
                    datas['priority'] = int(queues['PRIORITYTIER'])
                    datas['default'] = True \
                        if queues['DEFAULT'] == 'YES' else False
                    datas['user_groups'] = [queues['ALLOWGROUPS']]
                    datas['nodes_total'] = {node_state: query['nodes']}
                    datas['nodes_list'] = {node_state: query['node_list']}
                    datas['max_time'] = queues['MAXTIME']
                    datas['over_subscribe'] = queues['OVERSUBSCRIBE']
                    data[queue_name] = datas
                else:
                    data[queue_name]['nodes_total'][node_state] = \
                        query['nodes']
                    data[queue_name]['nodes_list'][node_state] = \
                        query['node_list']
        except BaseException:
            logger.exception("Get Queues Info Message Error")
            return None
        return data.values()[0] if len(data) > 0 else {}

    @staticmethod
    def update_queues_detail(queue_name, data):
        import subprocess
        node_list = data['node_list']
        default = data['default']
        priority = data['priority']
        max_time = data['max_time']
        over_subscribe = data['over_subscribe']
        user_groups = data['user_groups']
        avail = data['avail']

        node_list = node_list.replace(' ', ',')
        try:
            subprocess.check_call(['scontrol', 'show', 'Node', node_list],
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
        except BaseException:
            logger.exception("Node Name Not Exist.")
            raise NodeNotExistException
        try:
            default = 'YES' if default else 'NO'
            parameter = 'PartitionName={} Nodes={} Default={} Priority={} ' \
                        'MaxTime={} OverSubscribe={} AllowGroups={} State={}'\
                .format(queue_name, node_list, default, priority, max_time,
                        over_subscribe, ','.join(user_groups), avail).split()
            subprocess.check_call(['scontrol', 'update'] + parameter,
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
            SchedulerSlurm._save_slurm_conf()
        except BaseException:
            logger.exception("Update {} Queue Failed".format(queue_name))
            return None
        return True

    @staticmethod
    def delete_queues_detail(queue_name):
        import subprocess
        try:
            queue = subprocess.check_output(
                ['sinfo', '-p', queue_name],
                preexec_fn=SchedulerSlurm._set_gid_uid)
            is_used = subprocess.check_output(
                ['squeue', '-p', queue_name],
                preexec_fn=SchedulerSlurm._set_gid_uid)
        except BaseException:
            logger.exception("Search Queues Error")
            return None
        if len(queue.split('\n')[1]) <= 0:
            logger.error("Queues Name Not Exist.")
            return None
        if len(is_used.split('\n')[1]) > 0:
            logger.error("Queue is in use.")
            return None
        try:
            subprocess.check_call(
                ['scontrol', 'delete', 'PartitionName=' + queue_name],
                preexec_fn=SchedulerSlurm._set_gid_uid)
            SchedulerSlurm._save_slurm_conf()
        except BaseException:
            logger.exception("Delete {} Queue Failed".format(queue_name))
            return None
        return True

    @staticmethod
    def update_queues_state(queue_name, action):
        import subprocess
        try:
            parameter = 'PartitionName={} State={}'.format(
                queue_name, action).split()
            subprocess.check_call(['scontrol', 'update'] + parameter,
                                  preexec_fn=SchedulerSlurm._set_gid_uid)
            SchedulerSlurm._save_slurm_conf()
        except BaseException:
            logger.exception("Update {} Queue State Failed".format(queue_name))
            return None
        return True

    @staticmethod
    def _save_slurm_conf():
        import subprocess
        import shutil
        from os import path, remove

        def _set_root_gid_uid():
            os.setgid(0)
            os.setuid(0)
        try:
            new_config = subprocess.check_output(
                ['scontrol', 'write', 'config'],
                preexec_fn=_set_root_gid_uid)
            new_config_path = new_config.split()[4]
            slurm_conf_path = path.splitext(new_config_path)[0]
            shutil.copyfile(slurm_conf_path, slurm_conf_path + '.bk')
            with open(new_config_path, "r") as f,\
                    open(slurm_conf_path, 'w+') as f2:
                for line in f:
                    if line.strip() == 'CpuFreqDef=Unknown':
                        continue
                    else:
                        f2.write(line)
            remove(new_config_path)
        except:
            logger.exception("Save Slurm Conf Failed")

    @staticmethod
    def _set_gid_uid():
        slurm_user = settings.SLURM_USER.strip() \
            if len(settings.SLURM_USER.strip()) > 0 else 'root'
        uid = pwd.getpwnam(slurm_user).pw_uid
        gid = pwd.getpwnam(slurm_user).pw_gid
        os.setgid(gid)
        os.setuid(uid)

    @staticmethod
    def get_node_detail(node_list):
        import subprocess
        try:
            data = {'node_states': {}, 'details': ''}
            node_list = node_list.replace(' ', ',')
            details = subprocess.check_output(
                ["scontrol", "show", 'Node', node_list],
                preexec_fn=SchedulerSlurm._set_gid_uid)
            nodes = re.findall(r'NodeName=([^\s]+)', details, re.I)
            states = re.findall(r'State=([^\s]+)', details, re.I)
            data['details'] = details
            data['node_states']['nodes'] = nodes
            data['node_states']['states'] = states
        except BaseException:
            logger.exception("Get Nodes State Failed")
            return None
        return data
