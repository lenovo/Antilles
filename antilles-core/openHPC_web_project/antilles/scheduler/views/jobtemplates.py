# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import base64
import imghdr
import json
import logging
import os
import time

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from webconsole.rpc import RPCClient

from antilles.common.utils import json_schema_validate
from antilles.optlog.optlog import EventLog
from antilles.scheduler.exceptions import (
    InvalidLogoException, JobTemplateExistsException,
    LogoSizeTooLargeException, ParameterException, SubmitJobException,
    WorkspaceInvalidException,
)
from antilles.scheduler.models import Job, JobTemplate
from antilles.scheduler.utils import getcurrentuserinfo

logger = logging.getLogger(__name__)


class JobTemplateDetailView(APIView):
    """
    Retrieve, update or delete a JobTemplate instance.
    """

    def get(self, request, pk, format=None):
        # job_template = JobTemplate.objects.get(pk=pk, user_id=request.user.id)
        # User need to use the published template by others.
        job_template = JobTemplate.objects.get(pk=pk)
        data = job_template.as_dict()
        if data['user_id'] != request.user.id and data['type'] != 'public':
            return Response(status=status.HTTP_403_FORBIDDEN)
        workspace, billgroup = getcurrentuserinfo(request.user)
        data['workspace'] = workspace
        return Response(data)

    @json_schema_validate({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "logo": {"type": "string"},
            "parameters_json": {"type": "string"},
            "template_file": {"type": "string"},
            "desc": {"type": "string"}
        },
        "required": ["name", "logo", "parameters_json",
                     "template_file", "desc"]
    })
    def put(self, request, pk, format=None):
        if not request.user.workspace or request.user.workspace == '':
            raise WorkspaceInvalidException
        workspace, billgroup = getcurrentuserinfo(request.user)
        data = validate_job_template_params(request.data, workspace, pk)
        job_template = JobTemplate.objects.filter(id=pk,
                                                  user_id=request.user.id)
        job_template_key_list = [i.name for i in JobTemplate._meta.fields]
        new_job_template_dict = {
            k: v for k, v in data.iteritems() if k in job_template_key_list
            }
        if not new_job_template_dict['logo']:
            new_job_template_dict.pop('logo')

        job_template.update(**new_job_template_dict)
        job_template_updated = JobTemplate.objects.get(id=pk)
        return Response(job_template_updated.as_dict())

    def delete(self, request, pk, format=None):
        job_template = JobTemplate.objects.exclude(
            type='public').get(
            pk=pk, user_id=request.user.id)
        job_template.delete()
        return Response(job_template.as_dict(),
                        status=status.HTTP_204_NO_CONTENT)


class JobTemplateListView(APIView):
    """
    List all jobtemplates, or create a new jobtemplate.
    """

    def get(self, request, format=None):
        job_templates = JobTemplate.objects.filter(
            user_id=request.user.id).order_by('-create_time')
        serializer_data = [obj.as_dict() for obj in job_templates]
        public_templates = JobTemplate.objects.filter(
            type='public').exclude(
            user_id=request.user.id).order_by('-create_time')
        for template in public_templates:
            serializer_data.append(template.as_dict())
        result = []
        for data in serializer_data:
            data["parameters_json"] = ""
            data["template_file"] = ""
            result.append(data)
        return Response({'data': result})

    @json_schema_validate({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "logo": {"type": "string"},
            "parameters_json": {"type": "string"},
            "template_file": {"type": "string"},
            "desc": {"type": "string"}
        },
        "required": ["name", "logo", "parameters_json",
                     "template_file", "desc"]
    })
    def post(self, request, format=None):
        # user = request.user.username
        if not request.user.workspace or request.user.workspace == '':
            raise WorkspaceInvalidException
        workspace, billgroup = getcurrentuserinfo(request.user)
        data = validate_job_template_params(request.data, workspace)
        if not data:
            raise SubmitJobException
        data['user_id'] = request.user.id
        data['scheduler'] = 'slurm'
        data['type'] = 'private'
        job_template_key_list = [i.name for i in JobTemplate._meta.fields]
        new_job_template_dict = {
            k: v for k, v in data.iteritems() if k in job_template_key_list
            }
        jobtemplate_created = JobTemplate.objects.create(
            **new_job_template_dict)
        return Response(
            jobtemplate_created.as_dict(),
            status=status.HTTP_201_CREATED)


class JobTemplatePublishView(APIView):
    @json_schema_validate({
        "type": "object",
        "properties": {
            "category": {"type": "string"},
        },
        "required": ["category"]
    })
    def post(self, request, pk, format=None):
        data = request.data
        job_template = JobTemplate.objects.exclude(
            type='public').get(
            pk=pk, user_id=request.user.id)
        job_template.type = 'public'
        job_template.category = data['category']
        job_template.save()
        return Response(job_template.as_dict())


class JobTemplateUnpublishView(APIView):
    def post(self, request, pk, format=None):
        job_template = JobTemplate.objects.exclude(
            type='private').get(pk=pk, user_id=request.user.id)
        job_template.type = 'private'
        job_template.save()
        return Response(job_template.as_dict())


class JobExView(APIView):
    @json_schema_validate({
        "type": "object",
        "properties": {
            "resumejobid": {"type": "integer", "minimum": 0},
            "jobname": {"type": "string"},
            "parameters": {
                "type": "object",
                "properties": {
                    "job_name": {"type": "string"},
                    "job_queue": {"type": "string"},
                    "job_workspace": {"type": "string"},
                },
                "required": ["job_name", "job_queue", "job_workspace"]
            },
            "template_file": {"type": "string"},
            "template_id": {"type": ["integer", "string"]},
            "type": {"type": "string"},
            "workingdir": {"type": "string"},
        },
        "required": ["jobname", "parameters", "template_file",
                     "template_id", "type", "workingdir"]
    })
    def post(self, request, format=None):
        user = request.user.username
        workspace, billgroup = getcurrentuserinfo(request.user)
        data = request.data
        job_key_list = [i.name for i in Job._meta.fields]
        # action is create
        data["operatestatus"] = "creating"
        data["submiter"] = user
        data["workspace"] = workspace
        data["billgroup"] = billgroup
        data["qtime"] = int(time.time())
        data["json_body"] = json.dumps(request.data)

        if "resumejobid" in data and data["resumejobid"]:
            job = JobTemplate.objects.get(pk=data["resumejobid"],
                                          user_id=request.user.id)
            job.isdeleted = True
            job.save()
        new_job_dict = {
            k: v for k, v in data.iteritems() if k in job_key_list
            }
        new_job = Job.objects.create(**new_job_dict)
        data["id"] = new_job.id

        # letrain template
        if isinstance(data['template_id'], int):
            template_file = JobTemplate.objects.get(
                id=data['template_id']).template_file
        else:
            logger.error('Invalid template id')
            raise ParameterException

        jobfilename = self.validate_post(request,
                                         data,
                                         workspace,
                                         template_file)
        if not jobfilename:
            raise SubmitJobException
        data['jobfilename'] = jobfilename
        task = {"method": "create_job", "type": "job", "args": data}
        jsontask = json.dumps(task)
        RPCClient().cast("job", jsontask)

        # add  operationlog
        EventLog.opt_create(
            request.user.username, EventLog.job, EventLog.create,
            EventLog.make_list(
                new_job.id, new_job.jobname)
        )
        return Response(data, status=status.HTTP_201_CREATED)

    def validate_post(self, request, data, workspace, template_file):
        jobfile_prefix = time.strftime("%Y%m%d%H%M", time.localtime())
        working_dir = os.path.join(
            workspace, data['workingdir'].replace(
                'MyFolder/', ''))
        absjobfilename = os.path.join(working_dir, jobfile_prefix + '_' + data[
            'jobname'] + '_' + str(data['id']) + ".slurm")
        f_cache = self.__rule_job_file(data, template_file, workspace)
        self.__generate_job_file(request, f_cache, data, absjobfilename)
        # absjobfilename is absolute path, change relative path
        jobfilename = absjobfilename.replace(workspace, 'MyFolder')
        return jobfilename

    def __generate_job_file(self, request, f_cache, data, absjobfilename):
        with open(absjobfilename, 'w') as file_handle:
            file_handle.write(f_cache)
        os.chown(absjobfilename, request.user.uid, request.user.group.gr_gid)

        return True

    def __rule_job_file(self, data, template_file, workspace):
        f_cache = ''

        data['parameters']['antilles'] = {
            'template_id': data['template_id'],
            'user_workspace': workspace,
        }

        # replace scheduler template
        template_file = self.__replace_scheduler_header(
            template_file, data['parameters'], settings.SCHEDULER_SOFTWARE)

        template_file = self.__replace_param(data['parameters'],
                                             template_file, workspace)

        f_cache += template_file
        return f_cache

    def __replace_param(self, parameters, template_file, workspace, prefix=''):
        for k, v in parameters.iteritems():
            if isinstance(v, dict):
                sub_prefix = '{}{}.'.format(prefix, k)
                template_file = self.__replace_param(v, template_file,
                                                     workspace, sub_prefix)
            else:
                parse_parameters = '{{%s%s}}' % (prefix, k)
                while parse_parameters in template_file:
                    if isinstance(v, bool):
                        v = 'true' if v else 'false'
                    elif (isinstance(v, unicode) or isinstance(v, str)) \
                            and v.startswith('MyFolder/'):
                        v = workspace + v.lstrip('MyFolder')
                    template_file = template_file.replace(parse_parameters,
                                                          str(v))
        return template_file

    def __replace_scheduler_header(self, template_file, parameters,
                                   sheduler='slurm'):
        sheduler_params = {
            '#ANTILLES.Job.Name': {
                'slurm': '#SBATCH --job-name=',
                'torque': '#PBS -N ',
                'lsf': '#BSUB -J ',
            },
            '#ANTILLES.Job.Workspace': {
                'slurm': '#SBATCH --workdir=',
                'torque': '#PBS -d ',
                'lsf': '#BSUB -cwd ',
            },
            '#ANTILLES.Job.Queue': {
                'slurm': '#SBATCH --partition=',
                'torque': '#PBS -q ',
                'lsf': '#BSUB -q ',
            },
            '#ANTILLES.Job.NumberOfNodes': {
                'slurm': '#SBATCH --nodes=',
                'torque': '#PBS -l nodes=',
                'lsf': 'BSUB -n ',
            },
            '#ANTILLES.Job.CpuPerNode': {
                'slurm': '#SBATCH --mincpus=',
                'torque': '#PBS -l ppn=',
                'lsf': '',
            },
            '#ANTILLES.Job.GpuPerNode': {
                'slurm': '#SBATCH --gres=gpu:',
                'torque': '',
                'lsf': '',
            },
            '#ANTILLES.Job.Exclusive': {
                'slurm': '#SBATCH --exclusive',
                'torque': '',
                'lsf': '',
            },
            '#ANTILLES.Job.TaskPerNode': {
                'slurm': '#SBATCH --ntasks-per-node=',
                'torque': '',
                'lsf': '',
            },
            '#ANTILLES.Job.CpuPerTask': {
                'slurm': '#SBATCH --cpus-per-task=',
                'torque': '',
                'lsf': '',
            },
        }

        if 'exclusive' in parameters and parameters['exclusive']:
            # exclusive mode, delete cpu limits
            template_file = template_file.replace(
                '#ANTILLES.Job.CpuPerNode={{cores_per_node}}\n', ''
            )
            template_file = template_file.replace(
                '#ANTILLES.Job.CpuPerTask={{cores_per_node}}\n', ''
            )
            template_file = template_file.replace(
                '#ANTILLES.Job.Exclusive={{exclusive}}\n',
                '#ANTILLES.Job.Exclusive=\n'
            )
        else:
            # non-exclusive mode, delete exclusive
            template_file = template_file.replace(
                '#ANTILLES.Job.Exclusive={{exclusive}}\n', '')

        template_file_list = template_file.split('\n')
        for line in template_file_list:
            if line.startswith('#ANTILLES'):
                # replace
                param_key = line.split('=')[0]
                template_file = template_file.replace(
                    param_key + '=', sheduler_params[param_key][sheduler])
            else:
                break
        if not template_file.startswith('#!/bin/bash'):
            template_file = '#!/bin/bash' + '\n' + template_file
        return template_file


def validate_job_template_params(data, workspace, pk=None):
    if pk is None:
        if JobTemplate.objects.filter(name=data['name']):
            raise JobTemplateExistsException
    else:
        objs = JobTemplate.objects.filter(name=data['name']).exclude(id=pk)
        if objs:
            raise JobTemplateExistsException
    if len(data['logo']) > 0:
        if(data['logo'].startswith('data:image/jpeg;base64,')):
            # After base64 the length can be increased 1.3 at most.
            if len(data['logo']) > 100 * 1024 * 1.3:
                raise LogoSizeTooLargeException
        else:
            logoImageFilename = data['logo']
            if logoImageFilename.startswith('MyFolder/'):
                logoImageFilename = logoImageFilename.replace('MyFolder/', '')
            logoImageFilename = os.path.join(workspace, logoImageFilename)
            if not imghdr.what(logoImageFilename):
                raise InvalidLogoException
            # not larger than 100KB( Original: 2M--2 * (1024 ** 2))
            if os.path.getsize(logoImageFilename) > 100 * 1024:
                raise LogoSizeTooLargeException
            # Encode pictures
            with open(logoImageFilename, 'rb') as f:
                data['logo'] = 'data:image/jpeg;base64,' \
                               + base64.b64encode(f.read())
    return data
