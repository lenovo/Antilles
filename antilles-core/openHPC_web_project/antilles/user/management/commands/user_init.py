# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import os
import sys

from django.core.management import BaseCommand

from ._util import print_red


class Command(BaseCommand):
    help = 'init user share dirs'

    def handle(self, *args, **options):

        from django.conf import settings
        share_dirs = settings.USER_SHARE_DIR

        if share_dirs:
            # create link to public share dir
            for des in share_dirs:
                src = os.path.abspath(des)
                dest = os.path.abspath(os.path.join('/etc/skel',
                                                    os.path.basename(des)))

                if not os.path.exists(dest):
                    try:
                        os.symlink(src, dest)
                    except OSError as e:
                        print_red('OSError: {}'.format(e))
                        sys.exit(1)
