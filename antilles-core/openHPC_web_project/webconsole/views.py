# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import commands
import subprocess
import logging
import time
import traceback
import json
import re
from collections import defaultdict
from os import path
from django.db.models import Sum

from django.core.cache import cache
from django.db.models import Count
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from webconsole.exceptions import ParameterException
from webconsole.files_manager import g_filesMgr

from antilles.common.utils import json_schema_validate
from antilles.cluster.models import Node
from antilles.scheduler.models import Job, JobConsole
from antilles.user.permissions import AsOperatorRole, AsUserRole
from webconsole.serializers.runningjob import JobRunningSerializer
from antilles.scheduler.models import RunningJob
from antilles.user.plugins import CookieAuthentication, JWTAuthentication


logger = logging.getLogger(__name__)

RESPONE_STATUS = ["success", "failed"]


class FilesConnector(APIView):
    authentication_classes = (
        JWTAuthentication,
        CookieAuthentication
    )

    def get(self, request):
        ret_data = g_filesMgr.run(request)

        from django.http import StreamingHttpResponse
        if isinstance(ret_data, StreamingHttpResponse):
            return ret_data
        else:
            return Response(data=ret_data, status=status.HTTP_200_OK)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "cmd": {"type": "string"}
        }
    })
    def post(self, request):
        ret_data = g_filesMgr.run(request)
        return Response(data=ret_data, status=status.HTTP_200_OK)


class JobHistoryView(APIView):
    """
    JobHistoryView
    Author: Benson
    """
    permission_classes = (AsOperatorRole,)

    # add function: wjq
    def filer_user(self, request, queryobjects):
        return queryobjects

    # ?query=count&&role=admin
    def get(self, request, format=None):
        from django.db.models import Q
        queryparams = request.GET
        try:
            num_of_points = int(queryparams.get("num_of_points"))
            if (num_of_points <= 0):
                raise ParameterException
            duration = int(queryparams.get("duration"))
            if (duration <= 0):
                raise ParameterException
            overall_status = queryparams.get("status")
            if not (overall_status in ["completed", "uncompleted"]):
                raise ParameterException
            q_name = "all"
            if (queryparams.get("q_name")):
                q_name = queryparams.get("q_name")
        except:
            logger.exception(traceback.format_exc())
            raise
        currentTime = time.time()
        deadtimes = []
        for i in range(num_of_points):
            deadtime = int(currentTime - duration +
                           duration / (num_of_points - 1) * i)
            deadtimes.append(deadtime)

        retdata = []
        jobs = Job.objects
        jobsource = self.filer_user(request, jobs)
        for deadtime in deadtimes:
            point = {}
            point["time"] = deadtime
            point["timezone"] = time.timezone
            if (overall_status == "uncompleted"):
                jobs = jobsource.filter(
                    Q(starttime__gt=0) & Q(starttime__lt=deadtime))
                jobs = jobs.filter(Q(endtime__gt=deadtime) | Q(endtime=0))
                if (q_name.lower() != "all"):
                    jobs = jobs.filter(queue__iexact=q_name)
                point["running"] = jobs.count()

                jobs = jobsource.filter(qtime__lt=deadtime)
                jobs = jobs.filter(Q(starttime__gt=deadtime)
                                   | (Q(starttime=0) & Q(endtime=0)))
                jobs = jobs.exclude(operatestatus="creating")
                if (q_name.lower() != "all"):
                    jobs = jobs.filter(queue__iexact=q_name)
                point["waiting"] = jobs.count()
            else:
                jobs = jobsource.filter(
                    Q(endtime__lt=deadtime) & Q(endtime__gt=0))
                if (q_name.lower() != "all"):
                    jobs = jobs.filter(queue__iexact=q_name)
                point["completed"] = jobs.count()

            retdata.append(point)
        return Response(retdata)


class JobHistoryViewUser(JobHistoryView):
    permission_classes = (AsUserRole,)

    def filer_user(self, request, queryobjects):
        username = request.user.username
        queryobjects = queryobjects.filter(submiter__exact=username)
        return queryobjects


class JobConsoleView(APIView):

    def get(self, request, job_id):
        try:
            console = JobConsole.objects.get(job_run_id=job_id).console_server
        except:
            logger.error(_("Can't get console for job: %s" % job_id))
            console = ""

        return Response(
            {
                'data': console
            }
        )

    @json_schema_validate({
        "type": "object",
        "properties": {
            "console": {"type": "string"}
        },
        "required": ["console"]
    })
    def post(self, request, job_id):
        console = request.data['console']
        logger.debug(_("update job: %(job_id)s, console: %(console)s" % ({
            "job_id": job_id,
            "console": console
        })))
        obj_list = JobConsole.objects.filter(job_run_id=job_id)
        if obj_list:
            obj_list.update(console_server=console)
        else:
            logger.info(_("Create job: %s in DB JobConsole" % job_id))
            JobConsole.objects.create(
                job_run_id=job_id, console_server=console)

        return Response(
            {
                'data': console
            }
        )


class JobLogView(APIView):

    def get(self, request):
        relative_path = request.GET.get('file_path')
        workspace = request.user.workspace
        file_path = path.join(workspace, relative_path)
        begin_line = first_line = int(request.GET.get('line_num'))
        number_of_lines = int(request.GET.get('lines', 1000))

        if (not path.isabs(relative_path)) and path.isfile(file_path):
            #total_line_num = int(
            #    commands.getoutput("wc -l %s | awk '{print $1}'" % file_path))
            # WC -L maybe miss one line if there is not /n
            # total_line_num = len(["" for line in open(file_path,"r")])
            f = open(file_path, "r")
            total_line = [line for line in f]
            total_line_num = len(total_line)
            if number_of_lines <= 0:
                temp_begin_value = 0
            else:
                temp_begin_value = total_line_num - number_of_lines
            if begin_line == 0:
                begin_line = 1 \
                    if temp_begin_value <= 0 else temp_begin_value + 1
            elif begin_line > 0:
                if begin_line < temp_begin_value:
                    begin_line = temp_begin_value + 1
                else:
                    begin_line += 1
            else:
                logger.error("error file line number: %s" % begin_line)
                begin_line = 1

            try_count = 99
            while try_count >= 0:
                logger.info("Try Count " + str(try_count))
                try_count -= 1
                log = ""
                if total_line_num > begin_line or\
                        (total_line_num == begin_line == 1
                         and first_line == 0):

                    for i in range(begin_line - 1, total_line_num):
                        log += total_line[i]

                # Must check if all threads have write to file
                not_sync = False
                for one_char in log:
                    if one_char == '\0':
                        not_sync = True
                        break
                if not_sync:
                    logger.info("Run sync...")
                    commands.getoutput("sync")
                    time.sleep(1)
                    continue
                else:
                    break
            # logger.debug("Get log data: %s, begin_line: %d, end_line: %d" %
            #               (log, begin_line, total_line_num))
            log_data = {"log": log.strip(), "line_num": total_line_num}
        else:
            logger.error(_("There is no file: %s" % file_path))
            log_data = {"log": "", "line_num": begin_line}
        return Response(
            {
                'data': log_data
            }
        )


class JobTemplateView(APIView):

    def get(self, request):
        user = request.user.username
        recent_jobs = Job.objects.filter(submiter=user).exclude(type='cmd').order_by('-qtime')[:100]
        data = defaultdict(int)
        for job in recent_jobs:
            job_type = job.type
            if job.type == 'file':
                json_body = json.loads(job.json_body)
                if 'template_id' in json_body:
                    if re.match('^(?:ai|letrain)_', str(json_body['template_id'])):
                        job_type = json_body['template_id']

            data[job_type] += 1

        return Response([{"type": item[0],
                          "counts": item[1]} for item in data.items() if data])


class JobHeatGpuView(APIView):
    def get_sql_query_data(self, table_name, hostname, used_table):
        query_sql = "select index,last(value) from hour.{table_name} \
        where host='{hostname}' and time > now() - 18s group by index;"\
        .format(table_name=table_name, hostname=hostname)
        used_sql = "select index,last(value) from hour.{table_name} \
        where host='{hostname}' and time > now() - 18s group by index;"\
        .format(table_name=used_table, hostname=hostname)
        sql = query_sql + used_sql
        used = []
        value = []
        logger.info("gpu heat sql: %s" % sql)
        data = cache.get(sql, epoch='s')
        value_data = []
        used_data = []
        try:
            for item in data[0]:
                value_data.append(item[0])

            for item in data[1]:
                used_data.append(item[0])

            for index, ivalue in enumerate(value_data):
                if used_data[index]['index'] == ivalue['index']:
                    use_flag = 1 if used_data[index]['last'] > 0 else 0
                    used.append(use_flag)
                    value.append(ivalue['last'])
        except Exception as e:
            logger.error(e.message)

        return used, value

    def trans_result(self, result, category, used_table):
        result = Node.objects.filter(hostname=result.split('*')[0].strip())
        if result:
            used, value = self.get_sql_query_data(
                category, result[0].hostname, used_table)
            return {
                'id': result[0].id,
                'hostname': result[0].hostname,
                'value': value,
                'used': used,
            }
        else:
            return

    def get(self, request, job_id, category, format=None):
        format_data = {"currentPage": 0, "offset": 0, "total": 0, "nodes": []}
        currentPage = int(request.GET["currentPage"])
        offset = int(request.GET["offset"])
        category_mapping = {
            'memory': 'node_gpu_mem_pct',
            'util': 'node_gpu_util',
            'temperature': 'node_gpu_temp'
        }
        used_table = 'node_gpu_process'
        try:
            jobs = Job.objects.get(id=int(job_id))
            gpusexechosts = jobs.gpusexechosts.split('+')
        except Exception:
            return Response(format_data, status=status.HTTP_200_OK)
        if category in category_mapping:
            category = category_mapping[category]
            ncnts = len(gpusexechosts)
            format_data["total"] = ncnts
            page_up_sum = offset * (currentPage - 1)
            start_idx = 0 if page_up_sum > ncnts else page_up_sum
            results = gpusexechosts[start_idx:start_idx + offset]
            format_data["offset"] = offset
            format_data["currentPage"] = currentPage
            format_data["nodes"] = [] if not gpusexechosts else \
                [self.trans_result(result, category, used_table)
                 for result in results]
        return Response(format_data, status=status.HTTP_200_OK)


class RunningJobDetailView(APIView):
    permission_classes = (AsOperatorRole,)

    def get_one_data(self, runningjobdict):
        mydata = {'url': '', 'jobid': '', 'queue': '',
                  'starttime': '', 'submiter': '', 'jobname': '', 'id': ''}
        data = runningjobdict.get('job')
        for item in mydata:
            mydata[item] = data[item]

        # Fix the num of cpu used by one job
        cpus = RunningJob.objects.filter(
            job__jobid=mydata["jobid"]).aggregate(cpu_used=Sum("core_num"))
        gpus = RunningJob.objects.filter(
            job__jobid=mydata["jobid"]).aggregate(gpu_used=Sum("gpu_num"))
        mydata['core_num_on_node'] = 0 if cpus["cpu_used"] == None else cpus["cpu_used"]
        mydata['gpu_num_on_node'] = 0 if gpus["gpu_used"] == None else gpus["gpu_used"]

        return mydata

    def get(self, request, pk, format=None):
        format_data = {"ret": RESPONE_STATUS[0], "msg": "", "jobs": []}
        responsedata = []
        node = Node.objects.get(id=pk)
        jobdata = RunningJob.objects.filter(node=node)
        serializerdata = JobRunningSerializer(
            jobdata, many=True, context={'request': request})
        data = serializerdata.data
        if len(data) > 0:
            for item in data:
                tem_data = self.get_one_data(item)
                responsedata.append(tem_data)
            else:
                format_data["jobs"] = responsedata
        return Response(format_data, status=status.HTTP_200_OK)
