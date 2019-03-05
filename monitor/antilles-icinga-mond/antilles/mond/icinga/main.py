# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import os
from ConfigParser import ConfigParser

from apscheduler.schedulers.background import BlockingScheduler

from antilles.tools.passwd import fetch_pass

from .datasource import DataSource
from .exceptions import ConfigFileNotExist
from .writer.influxdb_writer import InfluxDBWriter


def _unitize_domain(domains):
    domain_list = list()
    for domain in domains.split():
        domain = domain.strip()
        if not domain.startswith("."):
            domain = "." + domain
        domain_list.append(domain)

    return list(set(domain_list))


def parse_config():
    filepath = '/etc/antilles/icinga-mond.ini'

    if not os.path.exists(filepath):
        raise ConfigFileNotExist(filepath)

    config = ConfigParser()
    config.read(filepath)

    conf = dict()
    conf['base'] = dict(config.items('base'))
    conf['icinga'] = dict(config.items('icinga'))
    conf['postgresql'] = dict(config.items('postgresql'))
    conf['influxdb'] = dict(config.items('influxdb'))

    for section, option in conf.iteritems():
        for key, value in option.iteritems():
            conf[section][key] = value.strip()
            if section == "base" and key == "domain_filter":
                conf[section][key] = _unitize_domain(value)

    return conf


def monitor(recv_client, writer_client):
    writer_client.handle(recv_client.parse())


def main():
    config = parse_config()

    db_host = config['postgresql']['host']
    db_port = int(config['postgresql']['port'])
    db_name = config['postgresql']['database']

    api_account = fetch_pass(
        keyword='icinga2 api',
        host=db_host,
        port=db_port,
        db=db_name
    )

    influx_account = fetch_pass(
        keyword='influxdb',
        host=db_host,
        port=db_port,
        db=db_name
    )

    icinga_client = DataSource(
        host=config['icinga']['host'],
        port=int(config['icinga']['port']),
        user=api_account.user,
        password=api_account.passwd,
        service=config['base']['service'],
        attrs=config['icinga'].get('attributes', ''),
        api_v=config['icinga'].get('api_version', 'v1'),
        domain_filter=config['base'].get('domain_filter', list()),
        timeout=int(config['icinga']['timeout'])
    )

    writer_client = InfluxDBWriter(
        host=config['influxdb']['host'],
        port=int(config['influxdb']['port']),
        user=influx_account.user,
        password=influx_account.passwd,
        database=config['influxdb']['database'],
        timeout=int(config['influxdb']['timeout'])
    )

    scheduler = BlockingScheduler()
    interval = int(config['base'].get('sample_interval', '15'))
    scheduler.add_job(
        func=monitor,
        args=(icinga_client, writer_client),
        trigger="interval",
        seconds=interval,
        max_instances=1,
        id="antilles-monitoring"
    )
    scheduler.start()
