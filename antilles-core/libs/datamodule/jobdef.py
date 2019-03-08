# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""


import json


class Job(object):
    def __init__(self):
        self.id = "" #this is the id of the job in the db, not the jobid
        self.status = "" # this is the status to identify job is creating or deleting
        self.jobid = ""
        self.jobname = ""
        self.queue = ""
        self.qtime = 0
        self.starttime = 0
        self.endtime = 0
        self.submiter = ""
        self.submit_args = ""
        self.jobstatus = ""
        self.walltime = ""
        self.nodescount = 0
        self.cpuscount = 0
        self.priority = ""
        self.outfile = ""
        self.errfile = ""
        self.exechosts = ""
        self.type = "file"
        self.jobfilename = ""
        self.workingdir = ""
        self.mail = ""
        self.mailtrigger = ""
        self.pnodescount = 0
        self.ppn = 0
        self.pmem = 0
        self.isdeleted = False
        self.operatestatus = ""
        self.charge = 0
        self.wallduration = 0
        self.billgroup = ""
        self.workspace = ""
        self.hosts_cpus = ""
        self.gpuscount = 0
        self.gpuscharge = 0
        self.hosts_gpus = ""
        self.gpusexechosts = ""
        
    def tojson(self):
        obj = vars(self)
        return json.dumps(obj)


class CommonJob(Job):
    def __init__(self):
        Job.__init__(self)
        self.json_body = ""
