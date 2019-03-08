# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json

from services.job_service import JobService
import logging
logger = logging.getLogger(__name__)


class Dispatcher(object):
    def __init__(self):
        self.jobservice = JobService()

    def handle(self, taskMsg):
        task = None
        try:
            task = json.loads(taskMsg)
        except:
            logger.error("parse task msg error: %s", taskMsg)
        else:
            if task['type'] == 'job':
                self.jobservice.executeTask(task)
            else:
                logger.error('task is not supported: %s', taskMsg)
