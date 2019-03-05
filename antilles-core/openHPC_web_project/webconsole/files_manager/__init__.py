# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from connector import FilesConnector


class FilesManager(object):
    def run(self, request):
        connector = FilesConnector(request.user)

        src = request.query_params if request.method == "GET" else request.data
        cmd = src['cmd'] if src.has_key('cmd') else ''
        args = {}

        if not connector.commandExists(cmd):
            return {'error': connector.error(FilesConnector.ERROR_UNKNOWN_CMD)}

        # collect required arguments to exec command
        for (name, req) in connector.commandArgsList(cmd).items():
            arg = ''
            if name == 'targets':
                arg = src.getlist('targets[]')
            elif name == 'FILES':
                arg = src.getlist('upload[]')
            else:
                arg = src[name] if src.has_key(name) else ''

            if isinstance(arg, basestring):
                arg = arg.strip()

            if req and (name != 'content' and (arg == None or arg == '')):
                return {'error': connector.error(FilesConnector.ERROR_INV_PARAMS, cmd)}
            args[name] = arg

        return connector.execute(cmd, args)


g_filesMgr = FilesManager()
