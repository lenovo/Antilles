#! /usr/bin/python
# -*- coding:utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import socket
import tempfile
from distutils.archive_util import make_tarball
from distutils.dir_util import copy_tree, mkpath, remove_tree
from distutils.file_util import copy_file, write_file
from glob import iglob
from os import path
from subprocess import call

dictionary = tempfile.mktemp(prefix='antilles-data-', dir='.')
mkpath(dictionary)

try:
    # config file
    config_dictionary = path.join(dictionary, 'config')
    mkpath(config_dictionary)

    if path.exists('/etc/antilles'):
        copy_tree('/etc/antilles', path.join(config_dictionary, 'antilles'))

    if path.exists('/etc/ganglia'):
        copy_tree('/etc/ganglia', path.join(config_dictionary, 'ganglia'))

    if path.exists('/etc/influxdb'):
        copy_tree('/etc/influxdb', path.join(config_dictionary, 'influxdb'))

    if path.exists('/etc/slurm'):
        copy_tree('/etc/slurm', path.join(config_dictionary, 'slurm'))

    if path.exists('/etc/nginx'):
        copy_tree('/etc/nginx', path.join(config_dictionary, 'nginx'))

    if path.exists('/etc/openldap'):
        copy_tree('/etc/openldap', path.join(config_dictionary, 'openldap'))

    copy_tree('/etc/pam.d', path.join(config_dictionary, 'pam'))

    copy_file('/etc/hosts', config_dictionary)
    copy_file('/etc/resolv.conf', config_dictionary)
    copy_file('/etc/nslcd.conf', config_dictionary)
    copy_file('/etc/nsswitch.conf', config_dictionary)

    # host info
    info_dictionary = path.join(dictionary, 'info')
    mkpath(info_dictionary)

    write_file(
        path.join(info_dictionary, 'hostname'),
        [socket.gethostname()]
    )

    with open(path.join(info_dictionary, 'kernel'), 'w') as f:
        call(['sysctl', '-a'], stdout=f)

    with open(path.join(info_dictionary, 'rpm'), 'w') as f:
        call(['rpm', '-qa'], stdout=f)

    if path.exists('/usr/bin/pip'):
        with open(path.join(info_dictionary, 'pip'), 'w') as f:
            call(['/usr/bin/pip', 'list'], stdout=f)

    with open(path.join(info_dictionary, 'module'), 'w') as f:
        call(['bash', '--login', '-c', 'module list'], stdout=f)

    with open(path.join(info_dictionary, 'env'), 'w') as f:
        call(['env'], stdout=f)

    with open(path.join(info_dictionary, 'disk'), 'w') as f:
        call(['df', '-H'], stdout=f)

    with open(path.join(info_dictionary, 'systemd'), 'w') as f:
        call(['systemctl'], stdout=f)

    with open(path.join(info_dictionary, 'netstat'), 'w') as f:
        call(['netstat', '-anp'], stdout=f)

    with open(path.join(info_dictionary, 'user'), 'w') as f:
        call(['getent', 'passwd'], stdout=f)

    with open(path.join(info_dictionary, 'group'), 'w') as f:
        call(['getent', 'group'], stdout=f)

    # log file
    log_dictionary = path.join(dictionary, 'log')
    mkpath(log_dictionary)

    if path.exists('/var/log/antilles'):
        copy_tree('/var/log/antilles', path.join(log_dictionary, 'antilles'))

    if path.exists('/var/log/nginx'):
        copy_tree('/var/log/nginx', path.join(log_dictionary, 'nginx'))

    if path.exists('/var/log/confluent'):
        copy_tree('/var/log/confluent', path.join(log_dictionary, 'confluent'))

    if path.exists('/var/log/rabbitmq'):
        copy_tree('/var/log/rabbitmq', path.join(log_dictionary, 'rabbitmq'))

    for f in iglob('/var/log/slurm*.log'):
        copy_file(f, path.join(log_dictionary, 'slurm'))

    # journal file
    journal_dictionary = path.join(dictionary, 'journal')
    mkpath(journal_dictionary)

    units = [
        'confluent', 'ntpd'
        'influxdb', 'gmond',
        'postgresql', 'slapd',
        'nginx', 'nslcd',
        'slurmd', 'slurmctld',
        'rabbitmq-server',
        'antilles',
        'antilles-ganglia-mond',
        'antilles-confluent-mond-power',
        'antilles-confluent-mond-health',
        'antilles-confluent-mond-temp',
        'antilles-vnc-mond-xvnc',
    ]

    for unit in units:
        with open(path.join(journal_dictionary, unit), 'w') as f:
            call(['journalctl', '-xe', '-u', unit], stdout=f)

    make_tarball(
        base_name=path.basename(dictionary),
        base_dir=dictionary
    )
finally:
    remove_tree(dictionary)
