# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import time
import traceback
import json
import copy
import threading
import Queue
import logging
from libs.util.dbutil import DBUtil
from libs.job.job_manager import JobManager
from job_daemon.job.job_mq_operations import g_ui_jobs, g_jobop_lock

logger = logging.getLogger(__name__)

g_uncompleted_jobs = set()

# The result of the prev job scanning.
g_prev_jobs = {}
# The jobs that need to update or insert to db.
# The Queue is thread safe.
g_need_update_jobs = Queue.Queue()

g_delay_jobs = {}
g_delay_jobs_lock = threading.RLock()

def update_job_to_db(job_temp):
    retdata = {}
    #print job_temp
    retdata["method"] = "update_job"
    if(job_temp.jobid!=""):
        args_dict = {}
        args_dict = json.loads(job_temp.tojson())
        #args_dict = json.dumps(vars(job_temp))
        retdata["args"] = args_dict
        DBUtil().invoke_save(retdata)
        logger.debug("Update the job " + job_temp.jobid)
    else:
        logger.error("job id is null! ")


def _clear_job_to_db(clear_jobs):
    retdata = {}
    retdata["method"] = "clear_jobs_by_jobid"
    if clear_jobs:
        retdata["args"] = {"jobids": clear_jobs}
        DBUtil().invoke_save(retdata)
        logger.debug("Clear the jobs: " + str(clear_jobs))


def _clear_invalid_job(latest_jobs):
    global g_uncompleted_jobs
    current_uncompleted_jobs = set()
    for jobid, data in latest_jobs.items():
        status = data['status']
        if status.lower() != 'c' and status.lower() != 'cancelled':
            current_uncompleted_jobs.add(jobid)
            g_uncompleted_jobs.add(jobid)
        elif jobid in g_uncompleted_jobs:
            g_uncompleted_jobs.remove(jobid)
    need_clear_jobs = g_uncompleted_jobs - current_uncompleted_jobs
    _clear_job_to_db(need_clear_jobs)


def execute_job_monitor():
    logger.debug("start one update circuit")
    try:
        current_jobs = JobManager().get_alljob_status_info()
        _clear_invalid_job(current_jobs)

        global g_prev_jobs, g_need_update_jobs
        for jobid in current_jobs:
            if jobid not in g_prev_jobs or current_jobs[jobid]['status'] != g_prev_jobs[jobid]['status']:
                if jobid in g_prev_jobs:
                    logger.debug('Job {} change status from {} to {}'.format(jobid, g_prev_jobs[jobid]['status'],
                                                        current_jobs[jobid]['status']))
                else:
                    logger.debug('Found new job {}'.format(jobid))
                dump_job = {jobid: copy.deepcopy(current_jobs[jobid])}
                g_need_update_jobs.put(dump_job)
        # The jobs that in the prev scan result but not in the current scan result
        # can be considered stop between two scanning.
        disappered_jobs = set(g_prev_jobs) - set(current_jobs)
        for jobid in disappered_jobs:
            if g_prev_jobs[jobid]['status'] != 'C':
                dump_job = {jobid: copy.deepcopy(g_prev_jobs[jobid])}
                dump_job[jobid]['status'] = 'C'
                g_need_update_jobs.put(dump_job)
        # Store the current scan result
        g_prev_jobs = copy.deepcopy(current_jobs)
    except:
        logger.error(traceback.format_exc())

def execute_db_updater():
    global g_need_update_jobs, g_delay_jobs, g_delay_jobs_lock
    while True:
        try:
            job = g_need_update_jobs.get(block=True, timeout=5)
            jobid = job.keys()[0]
            # Check whether this job is submitted from antilles
            find_in_ui_jobs = False
            with g_jobop_lock:
                if jobid in g_ui_jobs:
                    find_in_ui_jobs = True
                    if job[jobid]['status'] == 'C':
                        del g_ui_jobs[jobid]
            # The jobs that can not be decide as UI jobs need add to delay_jobs
            if find_in_ui_jobs:
                ui_job = JobManager().get_job(jobid, job[jobid])
                update_job_to_db(ui_job)
            else:
                with g_delay_jobs_lock:
                    if jobid not in g_delay_jobs:
                        g_delay_jobs[jobid] = {
                            'info': job[jobid]['info'],
                            'status': job[jobid]['status'],
                            'time': time.time()
                        }
                    else:
                        g_delay_jobs[jobid]['info'] = job[jobid]['info']
                        g_delay_jobs[jobid]['status'] = job[jobid]['status']
        except Queue.Empty:
            continue

def execute_delay_db_updater():
    global g_delay_jobs, g_delay_jobs_lock
    while True:
        ready_jobs = {}
        with g_delay_jobs_lock:
            for jobid in g_delay_jobs.keys():
                # Check whether this job is submitted from antilles
                find_in_ui_jobs = False
                with g_jobop_lock:
                    if jobid in g_ui_jobs:
                        find_in_ui_jobs = True
                        if job[jobid]['status'] == 'C':
                            del g_ui_jobs[jobid]
                        ready_jobs[jobid] = g_delay_jobs[jobid]
                # If still can not find in ui jobs, check timeout, default timeout is one minute
                if time.time() - g_delay_jobs[jobid]['time'] > 60:
                    ready_jobs[jobid] = g_delay_jobs[jobid]
                    ready_jobs[jobid]['cmd'] = True
            # Clear ready jobs from delay jobs, do this in the loop of delay jobs is not good.
            for jobid in ready_jobs.keys():
                if ready_jobs[jobid]['status'] == 'C':
                    del g_delay_jobs[jobid]
        # Store ready jobs into DB.
        for jobid in ready_jobs.keys():
            # Parse job scan result to job object.
            job = JobManager().get_job(jobid, ready_jobs[jobid])
            if job is not None:
                if 'cmd' in ready_jobs[jobid]:
                    job.type = 'cmd'
                update_job_to_db(job)
            else:
                logger.debug('Invalid job scan result.')
        # Sleep 2 seconds to let jobid be stored into g_ui_jobs
        time.sleep(2)
