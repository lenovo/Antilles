# -*- coding: utf-8 -*-

"""
Antilles Vnc Mond.

Usage:
    antilles-vnc-mond [options]
    antilles-vnc-mond (-h | --help)
    antilles-vnc-mond --version

Options:
    -h --help           Show this screen.
    --version           Show version.
    --config CONFIG
        Config file path.
        [default: /etc/antilles/vnc-mond.ini]

Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from ConfigParser import ConfigParser

from docopt import docopt
from pkg_resources import resource_filename

from .monitor import monitor


def main():
    arguments = docopt(__doc__, version='Antilles Vnc Mond 1.0.0')

    config = ConfigParser()
    config.read(resource_filename(__name__, 'data/default.ini'))
    filepath = arguments['--config']
    if filepath is None:
        filepath = '/etc/antilles/vnc-mond.ini'
    config.read(filepath)

    monitor(
        url=config.get('vnc', 'url'),
        timeout=config.getint('vnc', 'timeout')
    )
