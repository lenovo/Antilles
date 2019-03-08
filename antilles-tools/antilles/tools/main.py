# -*- coding: utf-8 -*-

"""
Antilles Password Management Tool

Usage:
  antilles-passwd-tool [options]
  antilles-passwd-tool (-h | --help)
  antilles-passwd-tool --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  --icinga              Configure icinga2 account.
  --dbname=DBNAME       Database name to connect to (default: "antilles").
  --host=HOSTNAME
        Database server host or socket directory (default: "local socket")
  --port=PORT           database server port (default: "5432")

Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import os

from docopt import docopt

from antilles.tools.passwd import start_guide


def main():
    arguments = docopt(__doc__, version='Antilles Password Management Tool 1.0.0')
    os.umask(0o077)
    dbname = 'antilles' if arguments['--dbname'] is None else arguments['--dbname']
    host = None if arguments['--host'] is None else arguments['--host']
    port = '5432' if arguments['--port'] is None else arguments['--port']
    start_guide(dbname, host, port, config_icinga=arguments['--icinga'])
