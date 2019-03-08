# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
from hashlib import md5

import paramiko
from falcon.errors import HTTPInternalServerError
from falcon.media.validators import jsonschema

logger = logging.getLogger(__name__)


class VncSession(object):
    def __init__(self, username, pid, name, port, index, host):
        self.username = username
        self.pid = pid
        self.name = name
        self.port = port
        self.index = index
        self.host = host

    @property
    def id(self):
        return md5(':'.join([
            self.username,
            str(self.pid),
            self.name,
            str(self.port),
            str(self.index),
            self.host,
        ])).hexdigest()

    def as_dict(self):
        return {
            'username': self.username,
            'pid': self.pid,
            'name': self.name,
            'port': self.port,
            'index': self.index,
            'host': self.host,
            'id': self.id,
        }

    def delete(self):
        import os
        import pwd
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, 22, pwd.getpwuid(os.getuid()).pw_name)
            stdin, stdout, stderr = ssh.exec_command(
                'vncserver -kill :{}'.format(self.index)
            )
            if len(stderr.readlines()) > 1:
                raise HTTPInternalServerError('Delete session failed.')


class VncManagerList(object):
    def __init__(self, session_data):
        self.session_data = session_data

    def on_get(self, req, resp, username=None):
        sessions = self.session_data.values()
        if username is not None:
            resp.media = [
                s.as_dict() for s in sessions
                if s.username == username
            ]
        else:
            resp.media = [
                s.as_dict() for s in sessions
            ]


class VncManagerDetail(object):
    def __init__(self, session_data):
        self.session_data = session_data

    def on_get(self, req, resp):
        # url /lookup?token=6a82ac3895ce45c5df54499bf94a5d23
        id = req.params.get('token', None)
        session = self.session_data[id]
        resp.media = {
            'host': session.host,
            'port': int(session.port),
        }

    def on_delete(self, req, resp, id):
        # url /session/{id}
        logger.info('delete session {0}'.format(id))
        self.session_data[id].delete()
        del self.session_data[id]

    @jsonschema.validate({
        'host': {
            'type': 'string'
        },
        'data': {
            'type': 'array',
            'minLength': 0,
            'items': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                    },
                    'name': {
                        'type': 'string',
                    },
                    'pid': {
                        'type': 'integer',
                        'minimum': 0
                    },
                    'host': {
                        'type': 'string',
                    },
                    'port': {
                        'type': 'integer',
                        'minimum': 0
                    },
                    'index': {
                        'type': 'integer',
                        'minimum': 0
                    },
                },
                'required': [
                    'username',
                    'name',
                    'pid',
                    'host',
                    'port',
                    'index'
                ]
            }
        }
    })
    def on_post(self, req, resp):
        host = req.media['host']
        sessions = req.media['data']
        indexes = []
        for session in sessions:
            logger.info('update_vnc_sessions %s', session)
            session = VncSession(**session)
            indexes.append(session.index)
            self.session_data[session.id] = session

        for id, session in self.session_data.items():
            if session.host == host and session.index not in indexes:
                del self.session_data[id]
