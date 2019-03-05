# -*- coding: utf-8 -*-
"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import tarfile
import uuid
from glob import iglob
from os import path

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from antilles.user.permissions import AsAdminRole


class WebLogView(APIView):
    permission_classes = (AsAdminRole,)

    def post(self, request):
        target = path.join(
            settings.DOWNLOAD_DIR, 'antilles-log-{}.tar.bz2'.format(uuid.uuid4())
        )

        with tarfile.open(target, 'w:bz2') as tf:
            for f in iglob(
                path.join(settings.LOG_DIR, '*.log')
            ):
                tf.add(f, path.join('antilles-log', path.basename(f)))

        return Response(
            data={'name': path.basename(target)}
        )
