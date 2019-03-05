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

from pkg_resources import yield_lines
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    install_requires = list(yield_lines(f.read()))

with open(path.join(here, 'test-requirements.txt')) as f:
    tests_require = list(yield_lines(f.read()))

setup(
    packages=find_packages(
        include=[
            'antilles*',
            'webconsole*'
        ]
    ),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'antilles = antilles.common.main:main',
        ],
    }
)
