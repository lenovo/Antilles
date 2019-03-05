# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import sys
import subprocess
import os
import tempfile

pip = subprocess.Popen(
    [
        'su', '-', sys.argv[1], '-c',
        "cd {0};{1}".format(sys.argv[3], sys.argv[2])
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
(stdout, stderr) = pip.communicate()


fd1, fn1 = tempfile.mkstemp(suffix='.log', prefix='openhpc_stdout_')
fd2, fn2 = tempfile.mkstemp(suffix='.log', prefix='openhpc_stderr_')
os.close(fd1)
os.close(fd2)
f1 = open(fn1, "w+")    
f1.write(stdout) 
f1.close() 
f2 = open(fn2, "w+")
f2.write(stderr)
f2.close()
print fn1
print fn2
