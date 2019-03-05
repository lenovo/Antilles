# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging
logger = logging.getLogger(__name__)


class OSUtil(object):
    @staticmethod
    def safe_popen(cmd, timeout=None, interval=10, **params):
        import os, subprocess, tempfile, time
        logger.debug(cmd)
        interval = interval
        # to get a temp file Name from system 
        fd1, fn1 = tempfile.mkstemp(suffix='.log', prefix='openhpc_stdout_')
        fd2, fn2 = tempfile.mkstemp(suffix='.log', prefix='openhpc_stderr_')
        os.close(fd1)
        os.close(fd2)

        f1 = None
        f2 = None
        try:
            rc = None
            pobj = subprocess.Popen(cmd, stdout=open(fn1, 'w'), stderr=open(fn2, 'w'))
            
            if timeout > 0:
                start = time.time()
                rc = pobj.poll()
                while rc is None:  # loop if process is still running
                    if timeout < time.time() - start:
                        pobj.kill()
                        break
                    time.sleep(interval)
                    rc = pobj.poll()
            else:
                rc = pobj.wait()
            
            outstr, errstr = '', ''
            try:
                f1 = open(fn1)          
                line = f1.readline()
                while line:    
                    outstr += line
                    line = f1.readline()
                f1.close()
                f1 = None
                os.remove(fn1)
                
                f2 = open(fn2)          
                line = f2.readline()
                while line:    
                    errstr += line
                    line = f2.readline()
                f2.close()
                f2 = None
                os.remove(fn2)
            except Exception:
                logger.error("exception")
            logger.debug(outstr)
            logger.debug(errstr)
            return rc, outstr, errstr
        finally:
            if f1 is not None:
                f1.close()
            if f2 is not None:
                f2.close()

