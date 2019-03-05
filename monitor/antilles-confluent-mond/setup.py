#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

"""The setup script."""

from os import path
from setuptools import setup, find_packages, Command
from pkg_resources import yield_lines

from distutils import log
from distutils.errors import DistutilsOptionError, DistutilsPlatformError

from glob import iglob

import os

here = path.abspath(path.dirname(__file__))


class bdist_rpm(Command):
    description = "create an RPM distribution"

    user_options = [
        ('spec-file=', None,
         "spec file to build rpm package"),

        ('bdist-base=', None,
         "base directory for creating built distributions"),
        ('rpm-base=', None,
         "base directory for creating RPMs (defaults to \"rpm\" under "
         "--bdist-base; must be specified for RPM 2)"),
        ('dist-dir=', 'd',
         "directory to put final RPM files in "
         "(and .spec files if --spec-only)"),
        ('source-only', None,
         "only generate source RPM"),
        ('binary-only', None,
         "only generate binary RPM"),
        ('use-bzip2', None,
         "use bzip2 instead of gzip to create source distribution"),

        # Actions to take when building RPM
        ('keep-temp', 'k',
         "don't clean up RPM build directory"),
        ('no-keep-temp', None,
         "clean up RPM build directory [default]"),

        # Allow a packager to explicitly force an architecture
        ('quiet', 'q',
         "Run the INSTALL phase of RPM building in quiet mode"),
    ]

    boolean_options = ['keep-temp', 'quiet']

    negative_opt = {'no-keep-temp': 'keep-temp'}

    def initialize_options(self):
        self.spec_file = None

        self.bdist_base = None
        self.rpm_base = None
        self.dist_dir = None
        self.binary_only = None
        self.source_only = None
        self.use_bzip2 = None

        self.keep_temp = 0
        self.quiet = 0

    def finalize_options(self):
        if self.spec_file is None:
            self.spec_file = '{0}.spec'.format(
                self.distribution.get_name()
            )

        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        if self.rpm_base is None:
            self.rpm_base = path.join(self.bdist_base, "rpm")

        if os.name != 'posix':
            raise DistutilsPlatformError(
                "don't know how to create RPM "
                "distributions on platform {0}"
                .format(os.name)
            )
        if self.binary_only and self.source_only:
            raise DistutilsOptionError(
                  "cannot supply both '--source-only' and '--binary-only'"
            )

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

    def run(self):
        # make directories
        rpm_dir = {}
        for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
            rpm_dir[d] = os.path.join(self.rpm_base, d)
            self.mkpath(rpm_dir[d])

        # Make a source distribution and copy to SOURCES directory with
        # optional icon.
        saved_dist_files = self.distribution.dist_files[:]
        sdist = self.reinitialize_command('sdist')
        if self.use_bzip2:
            sdist.formats = ['bztar']
        else:
            sdist.formats = ['gztar']
        self.run_command('sdist')
        self.distribution.dist_files = saved_dist_files

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        # build package
        log.info("building RPMs")
        rpm_cmd = ['rpmbuild']

        if self.source_only:  # what kind of RPMs?
            rpm_cmd.append('-bs')
        elif self.binary_only:
            rpm_cmd.append('-bb')
        else:
            rpm_cmd.append('-ba')
        rpm_cmd.extend([
            '--define', '_topdir {0}'.format(os.path.abspath(self.rpm_base))
        ])
        if not self.keep_temp:
            rpm_cmd.append('--clean')

        if self.quiet:
            rpm_cmd.append('--quiet')

        rpm_cmd.append(self.spec_file)

        self.spawn(rpm_cmd)

        if not self.dry_run:
            if not self.binary_only:
                for srpm in iglob(
                    path.join(
                        rpm_dir['SRPMS'], '*.rpm'
                    )
                ):
                    self.move_file(srpm, self.dist_dir)

            if not self.source_only:
                for rpm in iglob(
                        path.join(
                            rpm_dir['RPMS'], '*/*.rpm'
                        )
                ):
                    self.move_file(rpm, self.dist_dir)

with open(path.join(here, 'requirements.txt')) as f:
    install_requires = list(yield_lines(f.read()))

setup(
    packages=find_packages(
        include=[
            'antilles*',
        ],
    ),
    namespace_packages=['antilles', 'antilles.mond'],
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    python_requires='~=2.7',
    entry_points={
        'console_scripts': [
            'antilles-confluent-mond = antilles.mond.confluent.main:main',
        ],
        'confluent_metric': [
            'temp= antilles.mond.confluent.metric:CpuTemperatureMetric',
            'power = antilles.mond.confluent.metric:PowerMetric',
            'health = antilles.mond.confluent.metric:HardwareHealthMetric',
            'state = antilles.mond.confluent.metric:NodeStateMetric',
        ],
    },
    extras_require={
        'antilles': [
            'confluent>=1.7.2'
        ],
        'original': [
            'confluent_server>=1.7.2',
            'confluent_client>=1.7.2'
        ]
    },
    cmdclass={
        'bdist_rpm': bdist_rpm
    },
)
