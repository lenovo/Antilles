# -*- coding: utf-8 -*-

"""
Antilles Confluent Mond.

Usage:
    antilles-confluent-mond <metric> [options]
    antilles-confluent-mond (-h | --help)
    antilles-confluent-mond --version

Options:
    -h --help           Show this screen.
    --version           Show version.
    --config CONFIG
        Config file path.
        [default: /etc/antilles/confluent-mond.ini]

Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from ConfigParser import ConfigParser

from docopt import docopt
from influxdb import InfluxDBClient
from pkg_resources import load_entry_point, resource_filename

from antilles.tools.passwd import fetch_pass

from .hostlist import expand_hostlist


def main():
    arguments = docopt(__doc__, version='Antilles Confluent Mond 1.0.0')

    config = ConfigParser()
    config.read(resource_filename(__name__, 'data/default.ini'))
    filepath = arguments['--config']
    if filepath is None:
        filepath = '/etc/antilles/confluent-mond.ini'
    config.read(filepath)

    db_host = config.get('database', 'db_host')
    db_port = config.get('database', 'db_port')
    db_name = config.get('database', 'db_name')

    influxdb_account = fetch_pass(
        keyword='influxdb',
        host=db_host,
        port=db_port,
        db=db_name
    )
    username = influxdb_account.user
    password = influxdb_account.passwd

    confluent_account = fetch_pass(
        keyword='confluent',
        host=db_host,
        port=db_port,
        db=db_name
    )

    influx = InfluxDBClient(
        host=config.get('influxdb', 'host'),
        port=config.getint('influxdb', 'port'),
        username=username,
        password=password,
        database=config.get('influxdb', 'database'),
        timeout=config.getint('influxdb', 'timeout')
    )

    plugin = load_entry_point(
        dist='antilles-confluent-mond',
        group='confluent_metric',
        name=arguments.get('<metric>')
    )

    server = config.get('confluent', 'server')

    metric = plugin(
        noderange=config.get('confluent', 'noderange'),
        hostlist=expand_hostlist(config.get('influxdb', 'hostlist')),
        user=confluent_account.user,
        passwd=confluent_account.passwd,
        server=server if len(server) > 0 else None
    )

    influx.write_points(
        points=metric.get_points()
    )
