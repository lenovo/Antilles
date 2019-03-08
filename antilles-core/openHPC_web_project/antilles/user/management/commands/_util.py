# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""


def print_red(string):
    print('\033[31m{}\033[0m'.format(string))


def print_blue(string):
    print('\033[94m{}\033[0m'.format(string))


def print_green(string):
    print('\033[92m{}\033[0m'.format(string))


def print_gray(string):
    print('\033[37m{}\033[0m'.format(string))


def get_operator():
    import os
    import pwd
    import sys
    uid = os.getuid()
    try:
        username = pwd.getpwuid(uid).pw_name
    except Exception as e:
        print_red(e)
        sys.exit(1)

    if username != 'root':
        print_red("Permission denied.")
        sys.exit(1)

    import socket
    hostname = socket.gethostname()
    return 'CLI_USER: {}@{}'.format(username, hostname)
