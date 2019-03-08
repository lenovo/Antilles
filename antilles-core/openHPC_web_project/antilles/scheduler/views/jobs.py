# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
import json
import logging
import time

from django.conf import settings
from django.db.models import Case, IntegerField, Q, When
from django.db.models.functions import Cast
from django.http import Http404
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from webconsole.rpc import RPCClient

from antilles.common.helpers.filter_helper import get_users_from_filter
from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog
from antilles.scheduler.exceptions import (
    ParameterException, SubmitJobException,
)
from antilles.scheduler.models import Job
from antilles.user.permissions import AsOperatorRole, AsUserRole

logger = logging.getLogger(__name__)


class JobDetailView(APIView):
    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            logger.exception('job %s is not exists', pk)
            raise Http404

    def get(self, request, pk, format=None):
        queryparams = request.query_params
        job = self.get_object(pk)
        if queryparams.get("role") is None:
            if job.isdeleted:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(job.as_dict(), status=status.HTTP_200_OK)

    def _cancel_job(self, request, pk):
        user = request.user.username
        data = request.data
        queryparams = request.query_params
        if "action" not in data:
            raise ParameterException
        if data["action"] != "cancel":
            raise ParameterException

        job = self.get_object(pk)
        if queryparams.get("role") is None:
            if job.submiter != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if job.isdeleted:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if job.status != "running" and job.status != "waiting" \
                and job.status != "holding" and job.status != "suspending" \
                and job.status != "queueing":
            return Response({
                "message": "job is not in the state available for cancellation"
            }, status=status.HTTP_404_NOT_FOUND)
        job.operatestatus = "cancelling"
        job.save()

        task = {"method": "cancel_job", "type": "job"}
        task["args"] = {"user": user, "id": job.id, "jobid": job.jobid}
        jsontask = json.dumps(task)
        RPCClient().cast("job", jsontask)

        # add  operationlog
        EventLog.opt_create(
            request.user.username, EventLog.job, EventLog.cancel,
            EventLog.make_list(pk, job.jobname)
        )
        return Response({"id": job.id, "jobid": job.jobid,
                         "status": "cancelling"}, status=status.HTTP_200_OK)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "action": {"type": "string"}
        },
        "required": ["action"]
    })
    def put(self, request, pk, format=None):
        data = request.data
        if "action" not in data:
            raise ParameterException
        if data["action"] == "cancel":
            return self._cancel_job(request, pk)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        job = self.get_object(pk)
        user = request.user.username
        queryparams = request.query_params
        if queryparams.get("role") is None:
            if job.submiter != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        job.isdeleted = True
        job.save()

        # add  operationlog
        EventLog.opt_create(
            request.user.username, EventLog.job, EventLog.delete,
            EventLog.make_list(pk, job.jobname)
        )
        return Response(status=status.HTTP_200_OK)


class JobListView(APIView):

    def validate_file_job_data(self, data, type):
        if "jobfilename" not in data:
            return False
        if not isinstance(data["jobfilename"], basestring):
            return False
        data["jobfilename"] = data["jobfilename"].strip()
        if len(data["jobfilename"]) == 0:
            return False

        if "jobname" not in data:
            return False
        if not isinstance(data["jobname"], basestring):
            return False
        data["jobname"] = data["jobname"].strip()

        return True

    def validate_mail_data(self, data):
        if not isinstance(data["mail"], basestring):
            return False
        data["mail"] = data["mail"].strip()
        if len(data["mail"]) > 0:
            import re
            reg = re.compile(r'\S+@\S+')
            if not reg.match(data["mail"]):
                return False

        if not isinstance(data["mailtrigger"], basestring):
            return False
        data["mailtrigger"] = data["mailtrigger"].strip()
        mailtrigger = data["mailtrigger"]
        strlength = len(mailtrigger)
        if strlength > 0:
            if strlength > 3:
                return False
            for i in range(strlength):
                if mailtrigger[i] != 'a' and mailtrigger[i] != 'b' \
                        and mailtrigger[i] != 'e':
                    return False
            if mailtrigger.count("a") > 1 \
                    or mailtrigger.count("b") > 1 \
                    or mailtrigger.count("e") > 1:
                return False

        return True

    def validate_walltime_data(self, data):
        if not isinstance(data["walltime"], basestring):
            return False
        data["walltime"] = data["walltime"].strip()
        if len(data["walltime"]) > 0:
            ret = data["walltime"].split(":")
            if len(ret) != 3:
                return False
            if int(ret[1]) > 59 or int(ret[2]) > 59:
                return False
            if int(ret[0]) == 0 and int(ret[1]) == 0 \
                    and int(ret[2]) == 0:
                data["walltime"] = ""

        return True

    def validate_sche_param_data(self, data):
        if data["pnodescount"] is None:
            data["pnodescount"] = 0
        if not isinstance(data["pnodescount"], int):
            return False
        if data["ppn"] is None:
            data["ppn"] = 0
        if not isinstance(data["ppn"], int):
            return False
        if data["pmem"] is None:
            data["pmem"] = 0
        if not isinstance(data["pmem"], int):
            return False
        return True

    def validate_nonfile_job_data(self, data, type):
        from libs.util.confutil import ConfUtil
        if not ConfUtil.get_jobgen_script(type):
            return False

        if "queue" not in data \
                or "pnodescount" not in data \
                or "ppn" not in data \
                or "pmem" not in data \
                or "walltime" not in data \
                or "mail" not in data \
                or "mailtrigger" not in data:
            return False

        if not isinstance(data["queue"], basestring):
            return False
        data["queue"] = data["queue"].strip()
        if len(data["queue"]) == 0:
            return False

        if not self.validate_sche_param_data(data):
            return False

        if not self.validate_walltime_data(data):
            return False

        if not self.validate_mail_data(data):
            return False

        return True

    def validate_create_job_data(self, data):
        if "type" not in data:
            return False
        type = data["type"]
        if not isinstance(type, basestring):
            return False

        if type == "file":
            return self.validate_file_job_data(data, type)
        else:
            return self.validate_nonfile_job_data(data, type)

    def validate_post(self, data):
        if "action" not in data:
            return False
        action = data["action"]
        if not isinstance(action, basestring):
            return False
        if action != "create" and action != "rerun":
            return False

        if action == "create":
            return self.validate_create_job_data(data)
        elif action == "rerun":
            if "id" not in data:
                return False
            if not isinstance(data["id"], int):
                return False
        return True

    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise Http404

    def get_field(self, argss, mapping):
        if 'sort' not in argss:
            return ['id']
        order = argss["sort"]
        if order and order['prop'] == 'jobid':
            sql = Case(
                When(Q(jobid=''), then=-1),
                default=Cast('jobid', IntegerField())
            )
            return [sql.asc() if order['order'] == 'ascending' else sql.desc()]
        else:
            return [
                ('' if order['order'] == 'ascending' else '-') +
                mapping[order['prop']] if argss['sort'] is not None else 'id'
            ]

    def get_search_general(self, query, search, mapping):
        props = search['props']
        keyword = search['keyword'].strip()

        q = Q()
        for field in props:
            if field in mapping:
                prop = mapping[field]
            else:
                prop = field
            q |= Q(**{prop + '__icontains': keyword})

        return query.filter(q) if keyword != "" else query

    def get_search(self, query, search, mapping):
        return self.get_search_general(query, search, mapping)

    def filters(self, query, filters, mapping):
        if len(filters) > 0 and filters is not None:
            def change_time(filters):
                for field in filters:
                    values = []
                    if field['prop'] in \
                            ['qtime', 'endtime', 'walltime', 'starttime']:
                        for times in field['values']:
                            datetime1 = parse_datetime(times)
                            timestamap = time.mktime(datetime1.timetuple())
                            values.append(timestamap)
                        field['values'] = values
                return filters

            for field in change_time(filters):
                if field['prop'] in mapping:
                    prop = mapping[field['prop']]
                else:
                    prop = field['prop']

                if prop == "status" and "running" in field['values']:
                    # add job pause status to running list
                    query = query.filter(Q(**{
                        prop + '__{}'.format(field['type']): field['values']
                    })
                    ) if len(field['values']) > 0 else query
                elif prop == "status" and "cancelled" in field['values']:
                    query = query.filter(**{
                        prop + '__{}'.format(field['type']): field['values']
                    }) if len(field['values']) > 0 else query
                else:
                    query = query.filter(
                        **{
                            prop + '__{}'.format(
                                field['type']): field['values']
                        }
                    ) if len(field['values']) > 0 else query

        return query

    # ?status=running&&role=admin
    def get(self, request, format=None):

        user = request.user.username
        queryparams = request.query_params

        columns_mapping = {
            'id': 'id',
            'jobid': 'jobid',
            'jobname': 'jobname',
            'queue': 'queue',
            'qtime': 'qtime',
            'endtime': 'endtime',
            'walltime': 'walltime',
            'submiter': 'submiter',
            'starttime': 'starttime',
            'status': 'status',
            'jobstatus': 'jobstatus'
        }
        jobs = None
        argss = json.loads(queryparams['args'])

        jobs = Job.objects

        jobs = jobs.filter(isdeleted=False)
        role = queryparams.get('role', None)
        if role:
            if request.user.role >= AsOperatorRole.floor:
                # pass
                # Handler 'submiter' filter to compatible with following code
                for iter_filter in argss['filters']:
                    if iter_filter['prop'] == 'submiter':
                        iter_filter['values'] = \
                            get_users_from_filter(iter_filter)
                        iter_filter['value_type'] = 'username'
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            jobs = jobs.filter(submiter=user)

        jobs = self.filters(jobs, argss['filters'], columns_mapping)  # filter
        if 'search' in argss:
            search_data = argss['search']
            jobs = self.get_search(jobs, search_data, columns_mapping)
        filter_total = jobs.count()

        if self.get_field(argss, columns_mapping):
            jobs = jobs.order_by(*self.get_field(argss, columns_mapping))
        offset = int(argss['offset']) \
            if int(argss['offset']) < filter_total else 0

        jobs = jobs[offset:offset + int(argss['length'])].all()
        offset = offset + len(jobs)

        ret_jobs = []
        append = ret_jobs.append
        for job in jobs:
            append(job.as_dict(overview=True))

        return Response(
            {
                'total': filter_total,
                'offset': offset,
                'data': ret_jobs
            }
        )

    def getcurrentuserinfo(self, user):
        workspace = ""
        billgroup = ""
        try:
            workspace = user.workspace
            if workspace[-1] == '/' or workspace[-1] == "\\":
                workspace = workspace[0:-1]
            billgroup = user.bill_group.name
        except Exception:
            logger.exception(_("Error occured when creating bill group"))
            pass
        return workspace, billgroup

    @json_schema_validate({
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "jobname": {"type": "string"},
            "mail": {"type": "string", "format": "email"},
            "mailtrigger": {"type": "string"},
            "mpi_env_file": {"type": "string"},
            "mpi_prog": {"type": "string"},
            "mpi_run_arguments": {"type": "string"},
            "pmem": {"type": "integer"},
            "pnodescount": {"type": "integer"},
            "ppn": {"type": "integer"},
            "queue": {"type": "string"},
            "type": {"type": "string"},
            "walltime": {"type": "string"},
            "jobfilename": {"type": "string"},
            "id": {"type": "integer", "minimum": 0}
        },
        "required": ["action"]
    })
    def post(self, request, format=None):
        import time
        user = request.user.username
        workspace, billgroup = self.getcurrentuserinfo(request.user)

        data = request.data
        if not self.validate_post(data):
            raise SubmitJobException

        job_key_list = [i.name for i in Job._meta.fields]

        action = data["action"]
        if action == "create":
            data["operatestatus"] = "creating"
            data["submiter"] = user
            data["workspace"] = workspace
            data["billgroup"] = billgroup
            data["qtime"] = int(time.time())
            data["json_body"] = json.dumps(request.data)

            if "resumejobid" in data and data["resumejobid"]:
                job = self.get_object(data["resumejobid"])
                job.isdeleted = True
                job.save()

            try:
                new_job_dict = {
                    k: v for k, v in data.iteritems() if k in job_key_list
                }
                new_job = Job.objects.create(**new_job_dict)

                data["id"] = new_job.id
                task = {"method": "create_job", "type": "job"}
                task["args"] = data
                jsontask = json.dumps(task)
                RPCClient().cast("job", jsontask)

                # add  operationlog
                EventLog.opt_create(
                    request.user.username, EventLog.job, EventLog.create,
                    EventLog.make_list(
                        new_job.id, new_job.jobname)
                )
                return Response(data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error("create new job error: {}".format(e))

        elif action == "rerun":
            id = data["id"]
            job = self.get_object(id)

            data = job.as_dict()
            data.pop('id')
            data["operatestatus"] = "creating"
            data["jobstatus"] = ""
            data["submiter"] = user
            data["qtime"] = int(time.time())
            data["starttime"] = 0
            data["endtime"] = 0
            # data["type"] = "rerunjobid" + data["jobid"]
            data["jobid"] = ""
            data["workspace"] = workspace
            data["billgroup"] = billgroup

            try:
                rerun_job_dict = {
                    k: v for k, v in data.iteritems() if k in job_key_list
                }
                rerun_job = Job.objects.create(**rerun_job_dict)

                data["id"] = rerun_job.id
                task = {"method": "rerun_job", "type": "job"}
                task["args"] = data
                jsontask = json.dumps(task)
                RPCClient().cast("job", jsontask)

                # add link
                import os
                workingdir = data['workingdir'].replace("MyFolder",
                                                        data["workspace"], 1)
                output_temp = os.path.join(workingdir, '{}-{}.out')
                origin_output = output_temp.format(data["jobname"], id)
                present_output = output_temp.format(data["jobname"],
                                                    data["id"])
                # new add
                uid = request.user.uid
                gid = request.user.gid

                if os.path.exists(origin_output):
                    logger.debug(
                        origin_output + '__link to___' + present_output
                    )
                    os.symlink(origin_output, present_output)
                    # new add
                    os.lchown(present_output, uid, gid)
                    with open(origin_output, 'w'):
                        pass

                # add operationlog
                EventLog.opt_create(
                    request.user.username, EventLog.job, EventLog.rerun,
                    EventLog.make_list(rerun_job.id, rerun_job.jobname)
                )
                return Response(data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error("create rerun job error: {}".format(e))


class JobLatestViewUser(APIView):
    permission_classes = (AsUserRole,)

    # return  Q
    def filter_user(self, request):
        username = request.user.username
        return Q(submiter__exact=username)

    def get(self, request, format=None):
        queryparams = request.query_params.dict()
        counts = int(queryparams.get("counts", 0))
        job_status = queryparams.get("status", [])
        queryobject = Job.objects
        if job_status:
            job_status = job_status.split(',')

        userQ = self.filter_user(request)
        jobs = queryobject.filter(
            Q(status__in=job_status) & userQ
        ).order_by("-id")
        jobs = jobs[0:counts]

        ret_jobs = []
        append = ret_jobs.append
        for job in jobs:
            append(job.as_dict(overview=True))
        return Response(ret_jobs, status=status.HTTP_200_OK)


class JobLatestView(JobLatestViewUser):
    permission_classes = (AsOperatorRole,)

    def filter_user(self, request):
        return Q()
