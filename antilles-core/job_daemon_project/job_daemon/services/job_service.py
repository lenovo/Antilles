# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
import time
from django.conf import settings
from threading import Thread
import traceback
from job_daemon.job.job_mq_operations import JobMqOperations
from job_daemon.job.job_status_monitor import execute_job_monitor, execute_db_updater, execute_delay_db_updater

logger = logging.getLogger(__name__)


class JobWorkerThread(Thread):
    def __init__(self, task):
        Thread.__init__(self)
        self.task = task

    def run(self):
        call_method = self.task["method"]
        args = self.task["args"]
        logger.debug("start job worker " + call_method)
        callback = getattr(JobMqOperations, call_method)
        try:
            callback(args)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()


class JobMonitorThread(Thread):
    def run(self):
        while True:
            time.sleep(45)
            execute_job_monitor()


class DBUpdater(Thread):
    def run(self):
        execute_db_updater()


class DBDelayUpdater(Thread):
    def run(self):
        execute_delay_db_updater()


class JobService(object):
    def __init__(self):

        logger.debug("monitor job start")
        job_monitor = JobMonitorThread()
        job_monitor.start()
        db_updater = DBUpdater()
        db_updater.start()
        db_delay_updater = DBDelayUpdater()
        db_delay_updater.start()

    def executeTask(self, task):
        worker = JobWorkerThread(task)
        worker.start()
