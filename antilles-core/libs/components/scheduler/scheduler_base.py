# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from abc import ABCMeta
from six import add_metaclass


@add_metaclass(ABCMeta)
class SchedulerBase(object):
    '''
    classdocs
    '''
    def __init__(self):
        pass;

    @staticmethod
    def convert_hosts(hosts_str, average_gpu_num):
        pass

    @staticmethod
    def convert_job_status(lsfstatus):
        pass

    @staticmethod
    def convert_timestr_2_seconds(timestr):
        pass

    @staticmethod
    def get_alljob_status_info():
        pass

    #parse the output of scheduler command to return a job object
    #for torque, the command is "bjobs -UF jobid"
    @staticmethod
    def get_job(jobid, job_status_info=None):
        pass


    #using linux account 'user' to cancel one job
    #for torque, the command is "canceljob jobid"
    @staticmethod
    def cancel_job(jobid, user):
        pass

    #submit one job through jobfile
    #for torque the command is "qsub jobfile"
    @staticmethod
    def submit_job(abs_working_dir, abs_jobfile_name, user, jobname=None):
        pass

    @staticmethod
    def get_allqueues():
        pass

    @staticmethod
    def is_scheduler_working():
        pass

    @staticmethod
    def get_jobfile_suffix():
        pass

    @staticmethod
    def get_queues_info():
        pass

    @staticmethod
    def create_queues_info():
        pass

    @staticmethod
    def update_queues_state():
        pass

    @staticmethod
    def update_node_state():
        pass

    @staticmethod
    def get_node_detail():
        pass

    @staticmethod
    def get_queues_detail():
        pass

    @staticmethod
    def update_queues_detail():
        pass

    @staticmethod
    def delete_queues_detail():
        pass
