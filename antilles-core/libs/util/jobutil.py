# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from libs.util.osutil import OSUtil
import logging
import sys
import shlex

logger = logging.getLogger(__name__)

USER_HOME_DIR_ALIAS = "MyFolder"


class JobUtil(object):
    @staticmethod
    def convert_timestr_2_seconds(timestr):
        import time
        timeformat = "%a %b %d %H:%M:%S %Y"
        timestruct = time.strptime(timestr, timeformat)
        secs = time.mktime(timestruct)
        return int(secs)

    @staticmethod
    def convert_seconds_2_timestr(secs):
        import time
        timestr = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(secs))
        return timestr


    @staticmethod
    def exec_oscmd(cmd):
        cmd = shlex.split(cmd)
        rc,out,err = OSUtil.safe_popen(cmd)
        return rc,out,err


    @staticmethod
    def exec_oscmd_with_user(user, cmd):
        import os
        fullpath = os.path.abspath(os.path.dirname(__file__))
        if os.path.exists(fullpath +"/user_runcmd.py"):
            fullpath = fullpath +"/user_runcmd.py"
        else:
            fullpath = fullpath +"/user_runcmd.pyc"
        execmd = [str(sys.executable), str(fullpath), str(user), str(cmd)]
        rc,out,err = OSUtil.safe_popen(execmd)
        if len(err) == 0:
            try:
                fns = out.splitlines()
                fn1 = fns[0].strip()
                fn2 = fns[1].strip()
                f1 = open(fn1)
                out = f1.read()
                f1.close()
                os.remove(fn1)
                f2 = open(fn2)
                err = f2.read()
                f2.close()
                os.remove(fn2)
                logger.debug(out)
                logger.debug(err)
            except:
                import traceback
                logger.error(traceback.format_exc())
        return rc,out,err

    @staticmethod
    def exec_oscmd_with_user_underdir(user, cmd, sdir):
        import os
        fullpath = os.path.abspath(os.path.dirname(__file__))
        if os.path.exists(fullpath +"/user_runcmd_underdir.py"):
            fullpath = fullpath +"/user_runcmd_underdir.py"
        else:
            fullpath = fullpath +"/user_runcmd_underdir.pyc"
        execmd = [str(sys.executable), str(fullpath), str(user), cmd, sdir]
        rc,out,err = OSUtil.safe_popen(execmd)
        if len(err) == 0:
            try:
                fns = out.splitlines()
                fn1 = fns[0].strip()
                fn2 = fns[1].strip()
                f1 = open(fn1)
                out = f1.read()
                f1.close()
                os.remove(fn1)
                f2 = open(fn2)
                err = f2.read()
                f2.close()
                os.remove(fn2)
                logger.debug(out)
                logger.debug(err)
            except:
                import traceback
                logger.error(traceback.format_exc())
        return rc,out,err

    @staticmethod
    def get_real_path(path, workspace):
        relpath = path.replace(USER_HOME_DIR_ALIAS, workspace, 1)
        return relpath
